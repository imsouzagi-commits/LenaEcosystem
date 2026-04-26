from __future__ import annotations

import logging
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List

from openjarvis.core.types import Message, Role
from openjarvis.lena.action_center import ActionCenter
from openjarvis.lena.command_center import CommandCenter
from openjarvis.lena.memory_center import MemoryCenter
from openjarvis.lena.persona_center import PersonaCenter
from openjarvis.lena.temporal_center import TemporalCenter

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent / "cli"
MEMORY_PATH = BASE_DIR / "memory.json"


def _to_role(role_str: str) -> Role:
    mapping = {
        "user": Role.USER,
        "assistant": Role.ASSISTANT,
        "system": Role.SYSTEM,
    }
    return mapping.get(str(role_str).lower(), Role.USER)


class LenaKernel:
    def __init__(self, engine: Any = None, model: str | None = None):
        self.engine = engine
        self.default_model = model or "phi3:latest"

        if self.default_model == "qwen3.5:2b":
            self.default_model = "phi3:latest"

        self.memory = MemoryCenter(MEMORY_PATH)
        self.actions = ActionCenter()
        self.commands = CommandCenter(self.actions)
        self.temporal = TemporalCenter()
        self.persona = PersonaCenter()

        self.sessions: Dict[str, List[Dict[str, Any]]] = {}

        self.system_prompt = (
            "Você é Lena, uma assistente virtual premium.\n"
            "Responda sempre em português do Brasil.\n"
            "Fale curta, humana, natural, feminina e inteligente.\n"
            "Nunca gere listas automáticas.\n"
            "Nunca gere exemplos fictícios.\n"
            "Nunca gere prompts, instruções, treino, templates ou metatexto.\n"
            "Nunca invente contexto.\n"
            "Responda somente ao que o usuário disser.\n"
            "Seja conversacional e fluida.\n"
            "Máximo 3 frases.\n"
        )

    def _post_process(self, content: str) -> Dict[str, Any]:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": self.default_model,
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": content.strip(),
                    },
                    "finish_reason": "stop",
                    "index": 0,
                }
            ],
            "usage": {},
        }

    def _soft_idle_fallback(self) -> str:
        return self.persona.idle()

    def _is_bad_assistant_output(self, text: str) -> bool:
        lowered = str(text or "").lower().strip()

        bad_patterns = [
            "instruction:",
            "solution:",
            "training",
            "example:",
            "resposta à instrução",
            "como assistente",
            "usuário:",
            "assistant:",
            "human:",
            "---",
            "###",
            "prompt:",
            "template:",
        ]

        if not lowered:
            return True

        if any(p in lowered for p in bad_patterns):
            return True

        if len(lowered) > 350:
            return True

        if lowered.count("\n") > 4:
            return True

        return False

    def _sanitize_llm_output(self, text: str) -> str:
        cleaned = str(text or "").strip()

        if self._is_bad_assistant_output(cleaned):
            return self._soft_idle_fallback()

        return cleaned

    def _execute_llm(self, context: List[Dict[str, Any]]) -> str:
        if not self.engine:
            return self._soft_idle_fallback()

        messages = [
            Message(
                role=_to_role(msg.get("role", "user")),
                content=str(msg.get("content", "")),
            )
            for msg in context
        ]

        try:
            result = self.engine.generate(messages, model=self.default_model)
            content = str(result.get("content", "")).strip()
            return self._sanitize_llm_output(content)
        except Exception as exc:
            logger.error("LLM execution failed: %s", exc)
            return self._soft_idle_fallback()

    def _safe_session_extend(self, session_id: str, new_messages: List[Dict[str, Any]]) -> None:
        self.sessions[session_id].extend(new_messages)

        filtered: List[Dict[str, Any]] = []
        for item in self.sessions[session_id]:
            content = str(item.get("content", "")).strip()

            if not content:
                continue

            if item.get("role") == "assistant" and self._is_bad_assistant_output(content):
                continue

            filtered.append(item)

        self.sessions[session_id] = filtered[-24:]

    def _append_assistant_and_return(
        self,
        session_id: str,
        messages: List[Dict[str, Any]],
        content: str,
        cache_key: str,
    ) -> Dict[str, Any]:
        if messages:
            self._safe_session_extend(session_id, messages)

        self.sessions[session_id].append({"role": "assistant", "content": content})
        self.sessions[session_id] = self.sessions[session_id][-24:]

        final = self._post_process(content)
        self.memory.set_cache(cache_key, final)
        return final

    def _detect_intent(self, query: str) -> str:
        q = query.lower().strip()

        if q in {"oi", "olá", "ola", "oi lena", "lena"}:
            return "greeting"

        if any(x in q for x in ["boa noite", "bom dia", "boa tarde"]):
            return "greeting"

        if any(x in q for x in ["obrigado", "valeu", "thanks"]):
            return "gratitude"

        if any(x in q for x in ["estou cansado", "tô cansado", "estou triste", "tô triste", "estou mal", "exausto", "hoje foi ruim"]):
            return "emotional"

        if "o que você disse antes" in q or "repete" in q:
            return "followup"

        if any(x in q for x in ["qual é meu nome", "o que você sabe sobre mim", "do que eu gosto", "o que tenho amanhã"]):
            return "memory"

        return "generic"

    def _detect_user_repetition(self, session_id: str, raw_query: str) -> int:
        history = self.sessions.get(session_id, [])
        repeated = 0

        for item in reversed(history[-6:]):
            if item.get("role") != "user":
                continue

            if str(item.get("content", "")).strip().lower() == raw_query.strip().lower():
                repeated += 1
            else:
                break

        return repeated

    def _handle_repetition_case(self, repetition_count: int) -> str | None:
        if repetition_count <= 1:
            return None
        if repetition_count == 2:
            return "Oi, eu tô aqui."
        if repetition_count == 3:
            return "Tô te ouvindo, pode falar."
        if repetition_count >= 4:
            return "Você só quer minha atenção ou aconteceu alguma coisa?"
        return None

    def _handle_smalltalk(self, query: str) -> str | None:
        q = query.lower().strip()

        if q in {"tá aí", "ta ai", "lena tá aí", "lena ta ai"}:
            return "Tô aqui."

        if q in {"tudo bem", "tudo bem?", "como você tá", "como voce ta"}:
            return "Tô bem. E você?"

        if q in {"sumiu", "cadê você", "cade voce"}:
            return "Não sumi não."

        if q in {"nada", "...", "hm", "hmm", "sei lá", "sla"}:
            return "Tudo bem, pode falar quando quiser."

        return None

    def _handle_temporal_queries(self, query: str) -> str | None:
        q = query.lower()

        if "que horas" in q or "hora é" in q:
            return f"Agora são {self.temporal.now().strftime('%H:%M')}."

        if "que dia é hoje" in q or "data de hoje" in q:
            return f"Hoje é {self.temporal.today_name()}."

        if "amanhã que dia" in q:
            return f"Amanhã será {self.temporal.tomorrow_name()}."

        if "ontem que dia" in q:
            return f"Ontem foi {self.temporal.yesterday_name()}."

        return None

    def _handle_memory_queries(self, query: str) -> str | None:
        q = query.lower()

        if q.startswith(("registre ", "guarde ", "salve ", "lembre ")):
            memory_text = (
                query.replace("registre", "")
                .replace("guarde", "")
                .replace("salve", "")
                .replace("lembre", "")
                .strip()
            )
            self.memory.register_sacred(memory_text)
            self.memory.classify_profile_memory(memory_text)
            self.memory.save()
            return self.persona.memory_confirm()

        if "qual é meu nome" in q or "você sabe meu nome" in q:
            names = self.memory.user_profile.get("identity", [])
            if names:
                clean = names[-1].replace("meu nome é", "").replace("eu sou", "").strip()
                return f"Seu nome é {clean}."
            return "Você ainda não me disse seu nome."

        if "o que você sabe sobre mim" in q:
            memories = self.memory.recall_sacred()
            if memories:
                return "Eu lembro de você dizer: " + " | ".join(memories[-8:])
            return "Ainda tenho poucas coisas registradas sobre você."

        if "quais são meus gostos" in q or "do que eu gosto" in q:
            likes = self.memory.user_profile.get("likes", [])
            if likes:
                return "Você gosta de: " + " | ".join(likes[-8:])
            return "Ainda estou conhecendo seus gostos."

        if "quais compromissos eu tenho" in q or "o que tenho amanhã" in q:
            appointments = self.memory.user_profile.get("appointments", [])
            if appointments:
                return "Você tem registrado: " + " | ".join(appointments[-8:])
            return "Você não me passou compromissos recentes."

        return None

    def _handle_followup_context(self, session_id: str) -> str:
        history = self.sessions.get(session_id, [])

        for item in reversed(history):
            if item.get("role") == "assistant":
                previous = str(item.get("content", "")).strip()
                if previous:
                    return f"Eu disse: {previous}"

        return "Ainda não tinha falado nada antes."

    def _has_low_energy_state(self) -> bool:
        memories = self.memory.recall_long_term()
        markers = ["cansado", "triste", "mal", "exausto", "ruim"]
        return any(any(marker in item.lower() for marker in markers) for item in memories[-8:])

    def _try_memory_contextual_reply(self, query: str) -> str | None:
        q = query.lower()

        if "jantar" in q or "comer" in q:
            likes = self.memory.user_profile.get("likes", [])
            if likes:
                last_like = likes[-1].lower()

                if "sushi" in last_like:
                    return "Você gosta de sushi, então pode ser uma boa hoje."

                if "lasanha" in last_like:
                    return "Lasanha parece combinar com você hoje."

                if "café" in last_like:
                    return "Talvez algo leve e depois um café."

        return None

    def _handle_human_conversation(self, intent: str) -> str | None:
        if intent == "greeting":
            if self._has_low_energy_state():
                return self.persona.low_energy_hello()

            appointments = self.memory.user_profile.get("appointments", [])
            if appointments:
                return f"{self.persona.hello()} Não esquece que você comentou: {appointments[-1]}."

            return self.persona.hello()

        if intent == "gratitude":
            return self.persona.gratitude()

        if intent == "emotional":
            return self.persona.emotional_soft()

        return None

    def run(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not messages:
            return self._post_process("Entrada inválida.")

        self.memory.update(messages)

        session_id = "default"
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        self._safe_session_extend(session_id, messages)

        raw_query = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                raw_query = str(msg.get("content", "")).strip()
                break

        if not raw_query:
            return self._post_process("Não encontrei consulta válida.")

        cache_key = self.memory.make_cache_key(raw_query)
        cached = self.memory.get_cache(cache_key)
        if cached:
            return cached

        repetition_count = self._detect_user_repetition(session_id, raw_query)
        repetition_reply = self._handle_repetition_case(repetition_count)
        if repetition_reply:
            return self._append_assistant_and_return(session_id, [], repetition_reply, cache_key)

        smalltalk = self._handle_smalltalk(raw_query)
        if smalltalk:
            return self._append_assistant_and_return(session_id, [], smalltalk, cache_key)

        temporal_result = self._handle_temporal_queries(raw_query)
        if temporal_result:
            return self._append_assistant_and_return(session_id, [], temporal_result, cache_key)

        memory_result = self._handle_memory_queries(raw_query)
        if memory_result:
            return self._append_assistant_and_return(session_id, [], memory_result, cache_key)

        intent = self._detect_intent(raw_query)

        if intent == "followup":
            follow = self._handle_followup_context(session_id)
            return self._append_assistant_and_return(session_id, [], follow, cache_key)

        human_reply = self._handle_human_conversation(intent)
        if human_reply:
            return self._append_assistant_and_return(session_id, [], human_reply, cache_key)

        memory_context_reply = self._try_memory_contextual_reply(raw_query)
        if memory_context_reply:
            return self._append_assistant_and_return(session_id, [], memory_context_reply, cache_key)

        if self.commands.detect_local(raw_query):
            local_result = self.commands.execute(raw_query)
            if local_result:
                return self._append_assistant_and_return(session_id, [], local_result, cache_key)

        context = self.memory.build_context(self.system_prompt, self.sessions[session_id])
        llm_response = self._execute_llm(context)
        llm_response = self._sanitize_llm_output(llm_response)

        return self._append_assistant_and_return(session_id, [], llm_response, cache_key)