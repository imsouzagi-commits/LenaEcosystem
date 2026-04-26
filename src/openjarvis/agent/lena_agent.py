from __future__ import annotations

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import asyncio
import difflib
import hashlib
import json
import logging
import re
import subprocess
import time
import uuid
from collections import deque
from pathlib import Path
from typing import Any, Callable, Dict, List

from openjarvis.core.lena_state import lena_state
from openjarvis.core.registry import ModelRegistry
from openjarvis.core.types import Message, Role
from openjarvis.intelligence.intent_classifier import IntentClassifier
from openjarvis.intelligence.phonetic_command_rebuilder import PhoneticCommandRebuilder
from openjarvis.intelligence.voice_command_normalizer import VoiceCommandNormalizer
from openjarvis.learning.routing.router import DefaultQueryAnalyzer, HeuristicRouter
from openjarvis.plugins.open_url import open_url
from openjarvis.plugins.run_script import run_script

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent / "cli"
MEMORY_PATH = BASE_DIR / "memory.json"


def _to_role(role_str: str) -> Role:
    role_map = {
        "user": Role.USER,
        "assistant": Role.ASSISTANT,
        "system": Role.SYSTEM,
    }
    return role_map.get(role_str.lower(), Role.USER)


def _calculate_text_similarity(text1: str, text2: str) -> float:
    if not text1 or not text2:
        return 0.0

    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    return len(words1 & words2) / len(words1 | words2)


class LenaAgent:
    accepts_tools = True

    SYSTEM_LOCK_WORDS = {
        "wifi", "wi fi", "wi-fi", "internet", "rede", "network",
        "bluetooth",
        "volume", "som", "audio", "áudio", "sound",
        "brilho", "brightness", "screen", "tela",
        "mute", "microfone",
    }

    def __init__(self, engine: Any = None, model: str | None = None, **kwargs):
        self.engine = engine
        self.default_model = model or ""
        self.logger = logging.getLogger("LenaAgent")

        self.intent_classifier = None
        self.voice_normalizer = VoiceCommandNormalizer()
        self.command_rebuilder = PhoneticCommandRebuilder({})
        self.installed_apps = self._build_installed_apps_cache()

        self.memory = {
            "short_term": deque(maxlen=50),
            "long_term": [],
        }

        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
        self.response_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_keys_order = deque(maxlen=100)
        self.max_cache_size = 100

        self.available_tools: Dict[str, Callable] = {}
        self.register_tool("open_url", open_url)
        self.register_tool("run_script", run_script)

        self._load_long_term_memory()
        self.system_prompt = self._build_system_prompt()

        self.analyzer = DefaultQueryAnalyzer()
        self.router = HeuristicRouter(
            available_models=list(ModelRegistry.keys()),
            default_model=self.default_model,
            fallback_model=self.default_model,
        )

    def _build_system_prompt(self) -> str:
        return (
            "Você é Lena, assistente pessoal local.\n"
            "- Sempre responda em português do Brasil\n"
            "- Seja objetiva\n"
            "- Use contexto\n"
            "- Nunca invente\n"
        )

    def register_tool(self, name: str, func: Callable):
        self.available_tools[name] = func

    def get_intent_classifier(self) -> IntentClassifier:
        if self.intent_classifier is None:
            self.intent_classifier = IntentClassifier()
        return self.intent_classifier

    def _build_installed_apps_cache(self) -> Dict[str, str]:
        app_cache: Dict[str, str] = {
            "spotify": "Spotify",
            "ableton": "Ableton Live 12 Suite",
            "notes": "Notes",
            "notas": "Notes",
            "whatsapp": "WhatsApp",
            "safari": "Safari",
            "finder": "Finder",
            "chatgpt": "ChatGPT",
            "atlas": "ChatGPT",
        }

        applications_path = Path("/Applications")
        if applications_path.exists():
            try:
                for item in applications_path.iterdir():
                    if item.is_dir() and item.name.endswith(".app"):
                        clean = item.name.replace(".app", "").lower().strip()
                        app_cache[clean] = item.name.replace(".app", "")
            except Exception:
                pass

        return app_cache

    def fuzzy_match_app(self, query: str) -> str | None:
        if not query or query in self.SYSTEM_LOCK_WORDS:
            return None

        matches = difflib.get_close_matches(
            query.lower().strip(),
            self.installed_apps.keys(),
            n=1,
            cutoff=0.88,
        )
        return matches[0] if matches else None

    def resolve_app_name(self, spoken_target: str) -> str | None:
        if not spoken_target:
            return None

        spoken_target = spoken_target.lower().strip()

        if spoken_target in self.SYSTEM_LOCK_WORDS:
            return None

        if set(spoken_target.split()) & self.SYSTEM_LOCK_WORDS:
            return None

        exact = self.installed_apps.get(spoken_target)
        if exact:
            return exact

        fuzzy = self.fuzzy_match_app(spoken_target)
        if fuzzy:
            return self.installed_apps[fuzzy]

        return None

    def _safe_exec(self, command: List[str]) -> None:
        try:
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as exc:
            self.logger.debug(exc)

    def open_app(self, app_name: str) -> str:
        resolved = self.resolve_app_name(app_name)
        if not resolved:
            return f"App não encontrado: {app_name}"

        self._safe_exec(["open", "-a", resolved])
        return f"Abrindo {resolved}"

    def close_app(self, app_name: str) -> str:
        resolved = self.resolve_app_name(app_name)
        if not resolved:
            return f"App não encontrado: {app_name}"

        self._safe_exec(["osascript", "-e", f'tell application "{resolved}" to quit'])
        return f"Fechando {resolved}"

    def normalize_query(self, query: str) -> str:
        q = query.lower().strip()
        q = re.sub(r"[^\w\s]", "", q)

        replacements = {
            "abrir": "abre",
            "abra": "abre",
            "ligar": "liga",
            "ligue": "liga",
            "desligar": "desliga",
            "desligue": "desliga",
            "aumentar": "aumenta",
            "aumente": "aumenta",
            "subir": "aumenta",
            "abaixar": "abaixa",
            "abaixe": "abaixa",
            "diminuir": "abaixa",
            "som": "volume",
            "áudio": "volume",
            "audio": "volume",
            "wi fi": "wifi",
            "wi-fi": "wifi",
            "internet": "wifi",
            "tela": "brilho",
        }

        for old, new in replacements.items():
            q = re.sub(rf"\b{re.escape(old)}\b", new, q)

        q = re.sub(r"\blena\b", "", q)
        q = re.sub(r"\b(por favor|rapidinho|pra mim|pode|poderia|tem como)\b", "", q)

        return " ".join(q.split())

    def parse_commands(self, query: str) -> List[str]:
        protected = query.replace("wifi", "__WIFI__")
        raw = re.split(r"\s+\be\b\s+|\s+\band\b\s+|\s+\bthen\b\s+|,", protected)

        return [
            c.replace("__WIFI__", "wifi").strip()
            for c in raw
            if c.strip()
        ]

    def extract_command_target(self, command: str) -> tuple[str, str]:
        q = command.lower().strip()
        action = "unknown"

        patterns = {
            "abre": r"\babre\b",
            "fecha": r"\bfecha\b",
            "liga": r"\bliga\b",
            "desliga": r"\bdesliga\b",
            "aumenta": r"\baumenta\b",
            "abaixa": r"\babaixa\b",
        }

        for name, pattern in patterns.items():
            if re.search(pattern, q):
                action = name
                q = re.sub(pattern, "", q)
                break

        noise = {"o", "a", "os", "as", "um", "uma", "de", "do", "da"}
        target = " ".join([w for w in q.split() if w not in noise]).strip()

        return action, target

    def _execute_system_command(self, action: str, target: str) -> str | None:
        if "wifi" in target:
            self._safe_exec(["networksetup", "-setairportpower", "en0", "on" if action == "liga" else "off"])
            return "Ligando Wi-Fi" if action == "liga" else "Desligando Wi-Fi"

        if "volume" in target:
            script = (
                "set volume output volume ((output volume of (get volume settings)) + 10)"
                if action == "aumenta"
                else "set volume output volume ((output volume of (get volume settings)) - 10)"
            )
            self._safe_exec(["osascript", "-e", script])
            return "Aumentando volume" if action == "aumenta" else "Diminuindo volume"

        if "brilho" in target:
            self._safe_exec(["brightness", "0.8" if action == "aumenta" else "0.3"])
            return "Aumentando brilho" if action == "aumenta" else "Diminuindo brilho"

        return None

    def ultra_fast_local_detect(self, query: str) -> bool:
        return bool(re.search(
            r"\b(abre|fecha|liga|desliga|aumenta|abaixa|spotify|safari|finder|whatsapp|wifi|volume|brilho)\b",
            query.lower(),
        ))

    def handle_local_command(self, query: str) -> Dict[str, Any]:
        normalized = self.normalize_query(query)
        commands = self.parse_commands(normalized)
        results: List[str] = []

        for cmd in commands:
            action, target = self.extract_command_target(cmd)

            system_result = self._execute_system_command(action, target)
            if system_result:
                results.append(system_result)
                continue

            if action == "abre":
                results.append(self.open_app(target))
                continue

            if action == "fecha":
                results.append(self.close_app(target))
                continue

        final = " | ".join(results) if results else "Comando não reconhecido"

        return self.post_process(
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": final,
                        }
                    }
                ]
            },
            self.default_model,
        )

    def detect_tool_intent(self, query: str) -> str | None:
        if "http://" in query or "https://" in query:
            return "open_url"
        return None

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        return self.available_tools[tool_name](**arguments)

    def _generate_cache_key(self, query: str) -> str:
        return hashlib.sha256(query.strip().lower().encode()).hexdigest()[:16]

    def _load_long_term_memory(self):
        try:
            if MEMORY_PATH.exists():
                with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.memory["long_term"] = data if isinstance(data, list) else []
        except Exception:
            self.memory["long_term"] = []

    def _save_long_term_memory(self):
        try:
            MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(MEMORY_PATH, "w", encoding="utf-8") as f:
                json.dump(self.memory["long_term"], f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def validate_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {"role": m["role"], "content": str(m["content"])}
            for m in messages
            if isinstance(m, dict) and "role" in m and "content" in m
        ]

    def should_store_memory(self, message: str) -> bool:
        return any(k in message.lower() for k in ["meu nome", "gosto", "prefiro", "trabalho", "sou"])

    def update_memory(self, messages: List[Dict[str, Any]]):
        for msg in messages:
            self.memory["short_term"].append(msg)
            if self.should_store_memory(msg.get("content", "")):
                self.memory["long_term"].append(msg)
        self._save_long_term_memory()

    def build_context(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{"role": "system", "content": self.system_prompt}] + messages

    def select_model(self, context: List[Dict[str, Any]], query: str) -> str:
        return self.default_model

    def execute_model(self, model: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        if self.engine is None:
            return {"choices": [{"message": {"role": "assistant", "content": "Nenhum mecanismo configurado."}}]}

        messages = [
            Message(role=_to_role(m["role"]), content=m["content"])
            for m in context
        ]

        try:
            result = self.engine.generate(messages, model=model)
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": str(result.get("content", "")).strip(),
                        }
                    }
                ],
                "usage": result.get("usage", {}),
            }
        except Exception:
            return {"choices": [{"message": {"role": "assistant", "content": "Não consegui consultar o modelo agora."}}]}

    def post_process(self, response: Dict[str, Any], model: str) -> Dict[str, Any]:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": response.get("choices", []),
            "usage": response.get("usage", {}),
        }

    def _manage_cache(self, cache_key: str):
        if cache_key not in self.cache_keys_order:
            self.cache_keys_order.append(cache_key)

        while len(self.response_cache) > self.max_cache_size:
            oldest = self.cache_keys_order.popleft()
            self.response_cache.pop(oldest, None)

    def _process_request(self, valid_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        raw_query = ""
        for m in reversed(valid_messages):
            if m["role"] == "user":
                raw_query = m["content"]
                break

        rebuilt = self.command_rebuilder.rebuild(raw_query)
        rebuilt = self.voice_normalizer.normalize(rebuilt)
        normalized_query = self.normalize_query(rebuilt)

        if self.ultra_fast_local_detect(normalized_query):
            return self.handle_local_command(normalized_query)

        cache_key = self._generate_cache_key(normalized_query)
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]

        tool_name = self.detect_tool_intent(normalized_query)
        if tool_name:
            tool_result = self.execute_tool(tool_name, {"query": normalized_query})
            response = self.post_process(
                {"choices": [{"message": {"role": "assistant", "content": str(tool_result)}}]},
                self.default_model,
            )
            self.response_cache[cache_key] = response
            self._manage_cache(cache_key)
            return response

        context = self.build_context(valid_messages)
        selected_model = self.select_model(context, normalized_query)
        raw_response = self.execute_model(selected_model, context)
        final_response = self.post_process(raw_response, selected_model)

        self.response_cache[cache_key] = final_response
        self._manage_cache(cache_key)

        return final_response

    def run(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        valid_messages = self.validate_messages(messages)
        self.update_memory(valid_messages)
        return self._process_request(valid_messages)

    async def run_stream_async(self, messages: List[Dict[str, Any]]):
        response = self.run(messages)
        content = response["choices"][0]["message"]["content"]

        for token in content.split():
            chunk = {
                "id": f"chatcmpl-{uuid.uuid4().hex}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": self.default_model,
                "choices": [{"index": 0, "delta": {"content": token + " "}, "finish_reason": None}],
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            await asyncio.sleep(0.01)

        final_chunk = {
            "id": f"chatcmpl-{uuid.uuid4().hex}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": self.default_model,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"

    def run_stream(self, messages: List[Dict[str, Any]]):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        gen = self.run_stream_async(messages)

        try:
            while True:
                try:
                    yield loop.run_until_complete(gen.__anext__())
                except StopAsyncIteration:
                    break
        finally:
            loop.close()