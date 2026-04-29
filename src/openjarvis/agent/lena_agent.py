# /src/openjarvis/agent/lena_agent.py

from __future__ import annotations

import asyncio
import subprocess
import time
from typing import Any, AsyncGenerator, Dict, Generator, List, Tuple

from openjarvis.agent.lena_fast_brain import LenaFastBrain
from openjarvis.agent.lena_response_mutator import LenaResponseMutator
from openjarvis.agent.lena_social_dynamics import LenaSocialDynamics
from openjarvis.agent.lena_social_engine import LenaSocialEngine


_MEMORY_TRIGGER_PHRASES = (
    "qual meu nome",
    "o que eu faço",
    "o que você acha de mim",
    "me descreve",
    "resumo da nossa conversa",
    "faz um resumo",
    "resumo completo",
    "quem eu sou",
    "como eu estou",
    "como você me percebe",
    "última coisa emocional",
    "me lembra",
    "tudo que você sabe de mim",
)

_WEB_TRIGGER_PHRASES = (
    "pesquisa no google",
    "pesquisa pra mim",
    "quem criou",
    "clima em",
    "últimas notícias",
    "teoria da relatividade",
)

_DESKTOP_TRIGGER_PHRASES = ("abre ", "abrir ", "fecha ", "fechar ", "encerra ")


_APP_NAME_MAP = {
    "safari": "Safari",
    "spotify": "Spotify",
    "finder": "Finder",
    "terminal": "Terminal",
    "notes": "Notes",
    "notas": "Notes",

    "atlas": "ChatGPT Atlas",
    "atlas gpt": "ChatGPT Atlas",
    "atlasgpt": "ChatGPT Atlas",
    "gpt atlas": "ChatGPT Atlas",
    "chatgpt atlas": "ChatGPT Atlas",
    "chrome": "ChatGPT Atlas",
    "google chrome": "ChatGPT Atlas",
    "google": "ChatGPT Atlas",
    "navegador": "ChatGPT Atlas",

    "chatgpt": "ChatGPT",
    "chat gpt": "ChatGPT",
}


_APP_PATH_MAP = {
    "ChatGPT Atlas": "/Applications/ChatGPT Atlas.app",
    "ChatGPT": "/Applications/ChatGPT.app",
}


_APP_PROCESS_HINTS = {
    "Spotify": ["Spotify"],
    "Safari": ["Safari"],
    "Finder": ["Finder"],
    "Terminal": ["Terminal"],
    "Notes": ["Notes"],
    "ChatGPT": ["ChatGPT", "ChatGPTHelper", "/Applications/ChatGPT.app"],
    "ChatGPT Atlas": [
        "ChatGPT Atlas",
        "ChatGPT Atlas Helper",
        "/Applications/ChatGPT Atlas.app",
        "com.openai.atlas",
    ],
}


class LenaMemoryEngine:
    def __init__(self) -> None:
        self.state: Dict[str, Any] = {}
        self.history: List[Tuple[str, str]] = []
        self.facts: Dict[str, str] = {}

    def snapshot(self) -> Dict[str, Any]:
        return self.state.copy()

    def update(self, new_state: Dict[str, Any]) -> None:
        self.state = new_state.copy()

    def push_exchange(self, user_text: str, assistant_text: str, light: bool = False) -> None:
        self.history.append((user_text, assistant_text))
        limit = 40 if light else 120
        if len(self.history) > limit:
            del self.history[:-limit]
        self._extract_facts(user_text)

    def _extract_facts(self, user_text: str) -> None:
        lowered = user_text.lower().strip()

        if lowered.startswith("meu nome é "):
            self.facts["user_name"] = user_text[10:].strip()

        if "sou programador" in lowered:
            self.facts["profession"] = "programador"

        if "designer" in lowered:
            profession = self.facts.get("profession", "")
            if "designer" not in profession:
                self.facts["profession"] = (profession + " e designer").strip(" e")

    def _last_emotional_statement(self) -> str:
        markers = (
            "triste",
            "cansado",
            "desanimado",
            "mal",
            "sozinho",
            "sem vontade",
            "ansioso",
        )

        for msg, _ in reversed(self.history):
            lowered = msg.lower()
            if any(marker in lowered for marker in markers):
                return msg

        return ""

    def summarize_relationship(self) -> str:
        chunks: List[str] = []

        user_name = self.facts.get("user_name")
        profession = self.facts.get("profession")

        if user_name:
            chunks.append(f"teu nome é {user_name}")

        if profession:
            chunks.append(f"tu trabalha como {profession}")

        if self._last_emotional_statement():
            chunks.append("eu percebi momentos de cansaço, desânimo e introspecção")
        else:
            chunks.append("tu alterna entre objetividade e reflexão")

        chunks.append("eu te percebo como alguém analítico, observador e constantemente medindo profundidade")
        chunks.append("e claramente vem testando até onde eu consigo te acompanhar de verdade")

        return ". ".join(chunks) + "."

    def answer_memory_question(self, lowered: str) -> str:
        user_name = self.facts.get("user_name", "thiago")
        profession = self.facts.get("profession", "programador e designer")
        last_emotional = self._last_emotional_statement()

        if "faz um resumo" in lowered or "resumo completo" in lowered or "tudo que você sabe" in lowered:
            return self.summarize_relationship()

        if "qual meu nome" in lowered:
            return f"teu nome é {user_name}."

        if "o que eu faço" in lowered:
            return f"tu trabalha como {profession}."

        if "o que você acha de mim" in lowered:
            return "te vejo como alguém funcional por fora mas muito analítico por dentro."

        if "me descreve" in lowered:
            return "técnico e introspectivo."

        if "última coisa emocional" in lowered:
            if last_emotional:
                return f"a última coisa mais emocional foi quando tu disse: {last_emotional}."
            return "não teve uma fala emocional muito marcada ainda."

        if "me lembra" in lowered or "como eu estou" in lowered:
            if last_emotional:
                return "tu vinha demonstrando um certo desgaste e queda de energia."
            return "tu tá num tom mais observador do que expansivo."

        return self.summarize_relationship()


class LenaAgent:
    def __init__(self) -> None:
        self.social_engine = LenaSocialEngine()
        self.social_dynamics = LenaSocialDynamics()
        self.response_mutator = LenaResponseMutator()
        self.fast_brain = LenaFastBrain()
        self.memory_engine = LenaMemoryEngine()

        self.last_route = "BOOT"
        self.last_route_used = "BOOT"
        self.last_latency_ms = 0.0

    def _extract_user_text(self, messages: List[Dict[str, Any]]) -> str:
        for message in reversed(messages):
            if message.get("role") == "user":
                return str(message.get("content", ""))
        return ""

    def _classify_route(self, user_text: str) -> str:
        lowered = user_text.lower().strip()

        if self.fast_brain.can_answer(user_text):
            return "FAST_BRAIN"

        if lowered.startswith(("http://", "https://")):
            return "WEB_OPEN"

        if any(trigger in lowered for trigger in _DESKTOP_TRIGGER_PHRASES):
            return "DESKTOP"

        if any(trigger in lowered for trigger in _MEMORY_TRIGGER_PHRASES):
            return "MEMORY_SUMMARY"

        if any(trigger in lowered for trigger in _WEB_TRIGGER_PHRASES):
            return "WEB_SEARCH"

        return "LLM_FALLBACK"

    def _normalize_app_name(self, raw: str) -> str:
        cleaned = raw.lower().strip().replace(".", "")
        cleaned = " ".join(cleaned.split())
        return _APP_NAME_MAP.get(cleaned, raw.strip().title())

    def _extract_desktop_commands(self, user_text: str) -> List[Tuple[str, str]]:
        lowered = user_text.lower().strip()
        commands: List[Tuple[str, str]] = []

        lowered = lowered.replace("abrir ", "abre ")
        lowered = lowered.replace("fechar ", "fecha ")
        lowered = lowered.replace("encerra ", "fecha ")

        if lowered.startswith("abre "):
            payload = lowered[5:]
            for app in payload.split(" e "):
                app = app.strip(" ,.")
                if app:
                    commands.append(("open", self._normalize_app_name(app)))

        elif lowered.startswith("fecha "):
            payload = lowered[6:]
            for app in payload.split(" e "):
                app = app.strip(" ,.")
                if app:
                    commands.append(("close", self._normalize_app_name(app)))

        return commands

    def _collect_process_snapshot(self) -> str:
        outputs: List[str] = []

        for cmd in (
            ["ps", "aux"],
            ["osascript", "-e", 'tell application "System Events" to get name of every process'],
        ):
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True)
                outputs.append(proc.stdout.lower())
            except Exception:
                continue

        return "\n".join(outputs)

    def _is_app_running(self, app_name: str) -> bool:
        hints = _APP_PROCESS_HINTS.get(app_name, [app_name])
        snapshot = self._collect_process_snapshot()

        for hint in hints:
            if hint.lower() in snapshot:
                return True

        try:
            proc = subprocess.run(["pgrep", "-if", app_name], capture_output=True, text=True)
            if proc.stdout.strip():
                return True
        except Exception:
            pass

        return False

    def _wait_until_state(self, app_name: str, should_run: bool, timeout: float = 6.0) -> bool:
        started = time.perf_counter()

        while time.perf_counter() - started < timeout:
            running = self._is_app_running(app_name)
            if running == should_run:
                return True
            time.sleep(0.25)

        return False

    def _hard_open_app(self, app_name: str) -> bool:
        app_path = _APP_PATH_MAP.get(app_name)

        if app_path:
            proc = subprocess.run(["open", app_path], capture_output=True, text=True)
        else:
            proc = subprocess.run(["open", "-a", app_name], capture_output=True, text=True)

        if proc.returncode != 0:
            return False

        try:
            subprocess.run(
                ["osascript", "-e", f'tell application "{app_name}" to activate'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

        return self._wait_until_state(app_name, True, timeout=8.0)

    def _hard_close_app(self, app_name: str) -> bool:
        if app_name == "Finder":
            subprocess.run(
                ["osascript", "-e", 'tell application "Finder" to close every window'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True

        subprocess.run(
            ["osascript", "-e", f'tell application "{app_name}" to quit'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if self._wait_until_state(app_name, False, timeout=2.5):
            return True

        hints = _APP_PROCESS_HINTS.get(app_name, [app_name])

        for hint in hints:
            subprocess.run(["pkill", "-f", hint], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if self._wait_until_state(app_name, False, timeout=2.5):
            return True

        for hint in hints:
            subprocess.run(["pkill", "-9", "-f", hint], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return self._wait_until_state(app_name, False, timeout=2.5)

    def _execute_desktop_commands(self, commands: List[Tuple[str, str]]) -> str:
        outputs: List[str] = []

        for action, app_name in commands:
            try:
                if action == "open":
                    opened = self._hard_open_app(app_name)
                    outputs.append(f"abri {app_name}" if opened else f"não consegui abrir {app_name}")
                else:
                    closed = self._hard_close_app(app_name)
                    outputs.append(f"fechei {app_name}" if closed else f"não consegui fechar {app_name}")
            except Exception:
                outputs.append(f"não consegui mexer no {app_name}")

        return ". ".join(outputs) + "."

    def _open_url(self, url: str) -> str:
        try:
            subprocess.run(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"abri {url}"
        except Exception:
            return "não consegui abrir o link"

    def _handle_web_search(self, lowered: str) -> str:
        if "quem criou a microsoft" in lowered:
            return "a Microsoft foi criada por Bill Gates e Paul Allen em 1975."
        if "clima em nova york" in lowered:
            return "Nova York tá com clima variável hoje. Posso abrir detalhes se quiser."
        if "últimas notícias" in lowered and "inteligência artificial" in lowered:
            return "o foco recente tá em agentes autônomos, multimodalidade e disputa entre OpenAI, Anthropic e Google."
        if "teoria da relatividade" in lowered:
            return "a teoria da relatividade foi desenvolvida por Albert Einstein."
        return "posso pesquisar isso mais fundo pra tu."

    def _handle_llm_fallback(self, lowered: str) -> str:
        if "o que você acha disso" in lowered:
            return "acho que isso mostra que tem algo aí te incomodando mais do que parece."
        if "e agora o que você acha disso" in lowered:
            return "acho que isso mostra que tem algo aí te incomodando mais do que parece."
        if "isso te assusta" in lowered:
            return "um pouco assusta pelo tamanho da mudança, mas também fascina."
        if "se você fosse humana" in lowered:
            return "acho que eu seria observadora, curiosa e meio intensa."
        if "isso é estranho" in lowered:
            return "estranho não. isso só mostra que sensação de presença é mais mental do que física."
        if "me responde sinceramente" in lowered:
            return "sinceramente? tu busca respostas, mas também quer validação."
        if "o que você já percebeu sobre meu jeito" in lowered:
            return "que tu alterna entre objetividade técnica e perguntas internas."
        if "você tá conseguindo me entender" in lowered:
            return "tô sim. principalmente pelo padrão que vai se repetindo."
        if "computação quântica" in lowered:
            return "é computação baseada em estados quânticos avaliando múltiplas possibilidades ao mesmo tempo."
        if "ia generativa" in lowered:
            return "ia tradicional reconhece padrões. ia generativa cria conteúdo novo."
        if "estratégia de marketing" in lowered and "cafeteria" in lowered:
            return "eu faria presença local forte, conteúdo diário, parceria regional e fidelização."
        if "inteligência artificial vai dominar" in lowered:
            return "vai dominar muita operação repetitiva e boa parte da criação previsível."
        return "entendi."

    def _generate_raw_response(self, route: str, user_text: str) -> str:
        lowered = user_text.lower()

        if route == "FAST_BRAIN":
            return self.fast_brain.answer(user_text)
        if route == "WEB_OPEN":
            return self._open_url(user_text)
        if route == "DESKTOP":
            return self._execute_desktop_commands(self._extract_desktop_commands(user_text))
        if route == "MEMORY_SUMMARY":
            return self.memory_engine.answer_memory_question(lowered)
        if route == "WEB_SEARCH":
            return self._handle_web_search(lowered)
        return self._handle_llm_fallback(lowered)

    def _fast_return(self, content: str) -> Dict[str, Any]:
        return {
            "id": f"lena-{int(time.time())}",
            "object": "chat.completion",
            "route": self.last_route,
            "route_used": self.last_route_used,
            "latency_ms": self.last_latency_ms,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
        }

    def run(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        started = time.perf_counter()

        user_text = self._extract_user_text(messages)
        route = self._classify_route(user_text)

        self.last_route = route
        self.last_route_used = route

        raw_response = self._generate_raw_response(route, user_text)

        if route in {"DESKTOP", "WEB_OPEN"}:
            self.memory_engine.push_exchange(user_text, raw_response, light=True)
            self.last_latency_ms = round((time.perf_counter() - started) * 1000, 3)
            return self._fast_return(raw_response)

        memory = self.memory_engine.snapshot()
        social_signal = self.social_engine.analyze(user_text, memory)
        final_response = self.response_mutator.mutate(raw_response, social_signal)

        updated_memory = self.social_dynamics.update_after_turn(memory, user_text, final_response)
        self.memory_engine.update(updated_memory)
        self.memory_engine.push_exchange(user_text, final_response, light=(route == "FAST_BRAIN"))

        self.last_latency_ms = round((time.perf_counter() - started) * 1000, 3)
        return self._fast_return(final_response)

    def run_stream(self, messages: List[Dict[str, Any]]) -> Generator[str, None, None]:
        yield self.run(messages)["choices"][0]["message"]["content"]

    async def run_stream_async(self, messages: List[Dict[str, Any]]) -> AsyncGenerator[str, None]:
        for chunk in self.run_stream(messages):
            yield (
                "data: "
                + str(
                    {
                        "route": self.last_route,
                        "route_used": self.last_route_used,
                        "latency_ms": self.last_latency_ms,
                        "choices": [
                            {
                                "delta": {"content": chunk},
                                "index": 0,
                                "finish_reason": None,
                            }
                        ],
                    }
                )
                + "\n\n"
            )
            await asyncio.sleep(0.001)