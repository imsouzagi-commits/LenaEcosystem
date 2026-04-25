from __future__ import annotations

import asyncio
import logging
import time
import uuid
import json
import hashlib
import subprocess
import re
from typing import Optional, Any, Dict, List, Callable
from collections import deque
from pathlib import Path

from openjarvis.core.types import Message, Role
from openjarvis.core.registry import ModelRegistry
from openjarvis.learning.routing.router import DefaultQueryAnalyzer, HeuristicRouter
from openjarvis.plugins.open_url import open_url
from openjarvis.plugins.run_script import run_script
from openjarvis.intelligence.intent_classifier import IntentClassifier




logger = logging.getLogger(__name__)

# ==========================================
# Memory configuration for agent
# ==========================================
BASE_DIR = Path(__file__).parent.parent / "cli"
MEMORY_PATH = BASE_DIR / "memory.json"


def _to_role(role_str: str) -> Role:
    """Convert string role to Role enum."""
    role_map = {'user': Role.USER, 'assistant': Role.ASSISTANT, 'system': Role.SYSTEM}
    return role_map.get(role_str.lower(), Role.USER)


def _calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple word-overlap similarity score (Jaccard similarity).
    Used for intelligent memory retrieval.
    """
    if not text1 or not text2:
        return 0.0
    
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union) if union else 0.0


def estimate_prompt_tokens(messages: List[Message]) -> int:
    """Estimate token count for messages (simple approximation)."""
    total_chars = sum(len(m.content) for m in messages)
    # Rough estimate: ~4 characters per token
    return max(1, total_chars // 4)


# =========================
# LENA AGENT
# =========================
class LenaAgent:
    accepts_tools = True  # Enable tool support

    def __init__(self, engine: Any = None, model: str | None = None, **kwargs):
        self.engine = engine
        self.default_model = model or ""
        self.intent_classifier = IntentClassifier()

        # Logging
        self.logger = logging.getLogger("LenaAgent")

        # Memory
        self.memory = {
            "short_term": deque(maxlen=50),  # Buffer for recent messages
            "long_term": []  # Optional persistence (future: file/db)
        }
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}  # session_id -> history messages
        self.max_tokens_short = 4000  # Limit for short term
        self.max_tokens_long = 8000   # Limit for long term

        # Load long-term memory from file
        self._load_long_term_memory()

        # ==========================================
        # 🔥 MELHORIA #2: Cache profissional
        # ==========================================
        self.response_cache = {}
        self.cache_keys_order = deque(maxlen=100)  # FIFO order tracking
        self.max_cache_size = 100  # Limit cache to 100 items

        # Tools registry (extensible)
        self.available_tools: Dict[str, Callable] = {}  # name: Callable
        self.register_tool("open_url", open_url)
        self.register_tool("run_script", run_script)

        # ==========================================
        # 🔥 MELHORIA #7: System prompt melhorado
        # ==========================================
        self.system_prompt = self._build_system_prompt()

        # Routing
        self.analyzer = DefaultQueryAnalyzer()
        self.router = HeuristicRouter(
            available_models=list(ModelRegistry.keys()),
            default_model=self.default_model,
            fallback_model=self.default_model,
        )

    def fuzzy_match_app(self, query: str, app_map: dict) -> str | None:
        """
        Match aproximado para erros de digitação/voz.
        """
        import difflib

        words = query.split()

        for word in words:
            matches = difflib.get_close_matches(word, app_map.keys(), n=1, cutoff=0.6)
            if matches:
                return matches[0]

        return None

    def _build_system_prompt(self) -> str:
        return (
            "Você é Lena, uma assistente de IA.\n"
            "\n"
            "REGRAS OBRIGATÓRIAS:\n"
            "- Sempre responda em português do Brasil\n"
            "- Use o histórico da conversa para responder\n"
            "- Se o usuário perguntar sobre algo anterior, responda com base na última resposta do assistente\n"
            "- Não invente contexto\n"
            "- Não ignore mensagens anteriores\n"
            "- Não diga que é um ser humano\n"
            "- Não use separadores como '---'\n"
            "- Não faça suposições\n"
            "- Evite respostas vagas como 'como posso ajudar' sem contexto\n"
            "\n"
            "ESTILO:\n"
            "- Respostas curtas\n"
            "- Diretas\n"
            "- Linguagem simples\n"
        )

    def register_tool(self, name: str, func: Callable):
        """Register a tool function."""
        self.available_tools[name] = func
        self.logger.info(f"Registered tool: {name}")

    def detect_tool_intent(self, query: str) -> str | None:
        q = query.lower()

        if "http://" in q or "https://" in q:
            return "open_url"

        return None

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool with given arguments."""
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool {tool_name} not registered")
        
        tool_func = self.available_tools[tool_name]
        self.logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        try:
            result = tool_func(**arguments)
            self.logger.info(f"Tool {tool_name} executed successfully")
            return result
        except Exception as exc:
            self.logger.error(f"Tool {tool_name} execution failed: {exc}")
            raise

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions for model (OpenAI format)."""
        return []

    def normalize_query(self, query: str) -> str:
        """
        Normalize natural language query to standard intent.
        """
        import re
        
        q = query.lower().strip()
        q = re.sub(r"[^\w\s]", "", q) 

        # autocorreção leve (voz ruim)
        corrections = {
            "abri": "abre",
            "abrir": "abre",
            "abriça": "abre",
            "abdispotifai": "spotify",
            "spotfy": "spotify",
        }

        for wrong, correct in corrections.items():
            q = q.replace(wrong, correct)    

        fillers = [
            "por favor", "pra mim", "pode", "poderia",
            "rapidinho", "aí", "ai", "faz pra mim",
            "consegue", "queria", "tem como", "consegues"
        ]
        for filler in fillers:
            q = re.sub(rf"\b{re.escape(filler)}\b", "", q)
        
        q = re.sub(r"\blena\b", "", q)
        
        verb_map = {
            "abrir": "abre", "abra": "abre", "iniciar": "abre", "inicia": "abre",
            "ligar": "liga", "ligue": "liga", "desligar": "desliga", "desligue": "desliga",
            "aumentar": "aumenta", "aumente": "aumenta", "subir": "aumenta",
            "diminuir": "abaixa", "diminua": "abaixa", "baixar": "abaixa", "abaixe": "abaixa",
        }
        for verb_orig, verb_norm in verb_map.items():
            q = re.sub(rf"\b{verb_orig}\b", verb_norm, q)
        
        object_map = {
            "navegador": "safari", "internet": "safari", "som": "volume",
            "áudio": "volume", "audio": "volume", "wi-fi": "wifi", "wifi": "wifi",
            "brilho da tela": "brilho", "tela": "brilho",
        }
        for obj_orig, obj_norm in object_map.items():
            q = re.sub(rf"\b{re.escape(obj_orig)}\b", obj_norm, q)
        
        articles = ["o", "a", "os", "as", "um", "uma", "uns", "umas", "de", "do", "da"]
        for article in articles:
            q = re.sub(rf"\b{article}\b", "", q)
        
        q = " ".join(q.split())
        return q

    def detect_intent(self, query: str) -> str:
        """Detect user intent using ML-first approach with fallback."""
        import re

        q = query.lower().strip()

        # 🔥 STEP 1: ML prediction
        try:
            intent, confidence = self.intent_classifier.classify_with_confidence(q)
        except Exception:
            intent = self.intent_classifier.classify(q)
            confidence = 0.5  # fallback seguro

        # 🔥 STEP 2: confiança alta → usa ML
        if confidence >= 0.7:
            return intent

        # 🔥 STEP 3: fallback regex (backup only)
        if re.search(r"\b(abre|open|launch)\b", q):
            return "open"

        if re.search(r"\b(fecha|close|quit)\b", q):
            return "close"

        if re.search(r"\b(liga|on|ativa)\b", q):
            return "on"

        if re.search(r"\b(desliga|off|desativa)\b", q):
            return "off"

        if re.search(r"\b(aumenta|up|sobe)\b", q):
            return "up"

        if re.search(r"\b(abaixa|down|desce)\b", q):
            return "down"

        # 🔥 STEP 4: fallback final
        return intent if intent else "unknown"

    def route_query(self, query: str) -> str:
        """Route query to appropriate handler."""
        import re
        
        q = self.normalize_query(query)
        intent = self.detect_intent(q)

        if intent != "unknown":
            return "local"
        
        search_keywords = [r"\bnoticia", r"\bnotícia", r"\bhotel", r"\batual", r"\bweather", r"\btempo"]
        if any(re.search(kw, q) for kw in search_keywords):
            return "search"
        
        return "llm"
        
    def open_app(self, app_name: str) -> str:
        """Open application by name."""
        if not app_name or not isinstance(app_name, str):
            return "Nome de app inválido"

        applications_path = Path("/Applications")
        if not applications_path.exists():
            return "Diretório /Applications não encontrado"

        app_name_lower = app_name.lower().strip()
        candidates = []

        try:
            for item in applications_path.iterdir():
                if not item.is_dir() or not item.name.endswith(".app"):
                    continue

                item_name_lower = item.name.lower()
                bundle_name = item.name[:-4]

                score = 0

                if app_name_lower in item_name_lower:
                    score += 80
                if item_name_lower.startswith(app_name_lower):
                    score += 20

                words = item_name_lower.replace(".app", "").split()
                if app_name_lower in words:
                    score += 30

                if score > 0:
                    candidates.append((score, item, bundle_name))
        except Exception as e:
            self.logger.warning(f"Error scanning /Applications: {e}")
            return f"Erro ao procurar app: {str(e)}"

        if not candidates:
            return f"App não encontrado: {app_name}"

        candidates.sort(key=lambda x: x[0], reverse=True)
        _, best_path, best_name = candidates[0]

        app_clean_name = best_name.replace("Install ", "").strip()

        try:
            subprocess.run(["open", "-a", app_clean_name], check=True, timeout=5)
            self.logger.info(f"[LENA] Opening app resolved: {app_clean_name}")
            return f"Abrindo {app_clean_name}"
        except Exception:
            pass

        try:
            subprocess.run(["open", str(best_path)], check=True, timeout=5)
            self.logger.info(f"[LENA] Opening app fallback: {best_name}")
            return f"Abrindo {best_name}"
        except Exception as e:
            return f"Erro ao abrir app: {str(e)}"

    # =========================
    # 🔥 PARSER
    # =========================
    def parse_commands(self, query: str) -> List[str]:
        q = self.normalize_query(query)

        raw = re.split(r"\b(e|and|then|depois)\b|,", q)

        commands = [
        c.strip()
        for c in raw
        if c.strip() and c.strip() not in ["e", "and", "then", "depois", ","]
]

        self.logger.info(f"[CMD] Parsed → {commands}")
        return commands
        

    # =========================
    # 🔥 EXECUTOR SINGLE
    # =========================
    def execute_single_command(self, cmd: str) -> str:
        self.logger.info(f"[CMD] Executing: '{cmd}'")
        q = self.normalize_query(cmd)
        intent = self.detect_intent(q)

        aliases = {
            "ableton live": "ableton",
            "ableton suite": "ableton",
            "live 12": "ableton",
            "spotfy": "spotify",
            "spotify app": "spotify",
            "navegador": "safari",
            "internet": "safari",
        }

        for alias, real in aliases.items():
            q = re.sub(rf"\b{alias}\b", real, q)

        app_map = {
            "spotify": "Spotify",
            "ableton": "Ableton",
            "notes": "Notes",
            "notas": "Notes",
            "whatsapp": "WhatsApp",
            "safari": "Safari",
            "chatgpt": "ChatGPT",
            "atlas": "ChatGPT",
        }

        results = []

        # OPEN
        if intent == "open":
            app_found = None

            for app_key in app_map:
                if app_key in q:
                    app_found = app_key
                    break

            if not app_found:
                app_found = self.fuzzy_match_app(q, app_map)

            if app_found:
                return self.open_app(app_map[app_found])

            return f"App não encontrado: {cmd}"

        # CLOSE
        if intent == "close":
            for app_key in app_map:
                if app_key in q:
                    try:
                        subprocess.run(
                            ["osascript", "-e", f'tell application "{app_map[app_key]}" to quit'],
                            check=False,
                            timeout=5
                        )
                        return f"Fechando {app_map[app_key]}"
                    except Exception:
                        return f"Erro ao fechar {app_map[app_key]}"

        # VOLUME
        if "volume" in q:
            if intent == "up":
                subprocess.run([
                    "osascript", "-e",
                    "set volume output volume ((output volume of (get volume settings)) + 10)"
                ], check=False)
                return "Aumentando volume"

            if intent == "down":
                subprocess.run([
                    "osascript", "-e",
                    "set volume output volume ((output volume of (get volume settings)) - 10)"
                ], check=False)
                return "Diminuindo volume"

        # WIFI
        if "wifi" in q:
            if intent == "on":
                subprocess.run(["networksetup", "-setairportpower", "en0", "on"], check=False)
                return "Ligando Wi-Fi"

            if intent == "off":
                subprocess.run(["networksetup", "-setairportpower", "en0", "off"], check=False)
                return "Desligando Wi-Fi"

        return f"Não entendi: '{cmd}'"



    # =========================
    # 🔥 NOVO HANDLE (LIMPO)
    # =========================
    def handle_local_command(self, query: str) -> Dict[str, Any]:
        self.logger.info(f"[CMD] Incoming query: '{query}'")

        # 🔥 FIX 1: empty input
        if not query or not query.strip():
            return self.post_process({
                "choices": [{"message": {"content": "Comando não reconhecido"}}]
            }, self.default_model)

        commands = self.parse_commands(query)
        results = []

        for i, cmd in enumerate(commands):
            cmd = cmd.strip()

            if not cmd or len(cmd) < 2:
                continue

            try:
                result = self.execute_single_command(cmd)

                if result:
                    results.append(result)
                    self.logger.info(f"[CMD] Result: '{result}'")

                if i < len(commands) - 1:
                    time.sleep(0.3)

            except Exception as e:
                self.logger.warning(f"[CMD] Failed '{cmd}': {e}")

        # 🔥 FIX 2: fallback correto
        final = " | ".join(results) if results else "Comando não reconhecido"

        self.logger.info(f"[CMD] Final response: '{final}'")

        return self.post_process({
            "choices": [{"message": {"content": final}}]
        }, self.default_model)

        
    def retrieve_relevant_memory(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant messages from long-term memory using word-overlap similarity."""
        if not query or not self.memory["long_term"]:
            return []
        
        scored_messages = []
        for msg in self.memory["long_term"]:
            content = msg.get("content", "")
            if not content:
                continue
            
            score = _calculate_text_similarity(query, content)
            if score > 0.0:
                scored_messages.append((score, msg))
        
        scored_messages.sort(key=lambda x: x[0], reverse=True)
        relevant = [msg for score, msg in scored_messages[:top_k]]
        
        if relevant:
            self.logger.debug(
                f"Retrieved {len(relevant)} relevant memory messages from {len(self.memory['long_term'])} total "
                f"(top_k={top_k}, avg_score={sum(s for s, _ in scored_messages[:top_k]) / len(relevant):.2f})"
            )
        
        return relevant

    def _generate_cache_key(self, query: str) -> str:
        """Generate hash-based cache key from query."""
        normalized = query.strip().lower()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def _load_long_term_memory(self):
        """Load long-term memory from JSON file."""
        try:
            if MEMORY_PATH.exists():
                with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.memory["long_term"] = data
                        self.logger.info(
                            f"Loaded {len(data)} messages from long-term memory at {MEMORY_PATH}"
                        )
                    else:
                        self.logger.warning(
                            "Invalid memory.json format (expected list), starting with empty long-term memory"
                        )
                        self.memory["long_term"] = []
            else:
                self.logger.debug(
                    f"Memory file not found at {MEMORY_PATH}, starting with empty long-term memory"
                )
                self.memory["long_term"] = []
        except json.JSONDecodeError as exc:
            self.logger.error(f"Failed to parse memory.json: {exc}")
            self.memory["long_term"] = []
        except Exception as exc:
            self.logger.error(f"Failed to load long-term memory: {exc}")
            self.memory["long_term"] = []

    def _save_long_term_memory(self):
        """Save long-term memory to JSON file."""
        try:
            MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            with open(MEMORY_PATH, "w", encoding="utf-8") as f:
                json.dump(
                    self.memory["long_term"],
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            self.logger.debug(
                f"Saved {len(self.memory['long_term'])} messages to long-term memory at {MEMORY_PATH}"
            )
        except Exception as exc:
            self.logger.error(f"Failed to save long-term memory: {exc}")

    def validate_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and sanitize input messages."""
        if not messages or not isinstance(messages, list):
            self.logger.error("Invalid messages input: not a list or is empty")
            return []
        
        valid_messages = []
        for idx, msg in enumerate(messages):
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                content = msg.get("content", "")
                if not isinstance(content, str):
                    content = str(content)
                
                valid_messages.append({
                    "role": msg.get("role", "user"),
                    "content": content
                })
            else:
                self.logger.warning(f"Invalid message format at index {idx}: {msg}")
        
        return valid_messages

    def should_store_memory(self, message: str) -> bool:
        keywords = ["meu nome", "gosto", "prefiro", "trabalho", "sou"]
        return any(k in message.lower() for k in keywords)

    def update_memory(self, messages: List[Dict[str, Any]]):
        """Update short and long term memory with token limits."""
        for msg in messages:
            self.memory["short_term"].append(msg)
            if self.should_store_memory(msg.get("content", "")):
                self.memory["long_term"].append(msg)
        
        short_messages = [
            Message(role=_to_role(m['role']), content=str(m.get('content', '')))
            for m in self.memory["short_term"]
        ]
        short_tokens = estimate_prompt_tokens(short_messages)
        if short_tokens > self.max_tokens_short:
            while short_tokens > self.max_tokens_short and len(self.memory["short_term"]) > 1:
                self.memory["short_term"].popleft()
                short_messages = [
                    Message(role=_to_role(m['role']), content=str(m.get('content', '')))
                    for m in self.memory["short_term"]
                ]
                short_tokens = estimate_prompt_tokens(short_messages)
        
        long_messages = [
            Message(role=_to_role(m['role']), content=str(m.get('content', '')))
            for m in self.memory["long_term"]
        ]
        long_tokens = estimate_prompt_tokens(long_messages)
        if long_tokens > self.max_tokens_long:
            excess = long_tokens - self.max_tokens_long
            trim_count = 0
            while excess > 0 and trim_count < len(self.memory["long_term"]):
                excess -= len(self.memory["long_term"][trim_count].get("content", "")) // 4
                trim_count += 1
            self.memory["long_term"] = self.memory["long_term"][trim_count:]
        
        self._save_long_term_memory()

    def build_context(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        context = []
        context.append({"role": "system", "content": self.system_prompt})
        context.extend(messages)
        return context

    def select_model(self, context: List[Dict[str, Any]], query: str) -> str:
        """Select best model with improved routing."""
        return self.default_model

    def execute_model(self, model: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute model with robust compatibility for OpenJarvis engines."""
        max_retries = 2
        current_model = model

        messages = [
            Message(
                role=_to_role(m.get("role", "user")),
                content=str(m.get("content", ""))
            )
            for m in context
        ]

        context_size_chars = sum(len(m.content) for m in messages)
        self.logger.info(
            f"[LENA] Executing | model={current_model} | messages={len(messages)} | "
            f"context_size={context_size_chars} chars"
        )

        for attempt in range(max_retries + 1):
            try:
                self.logger.info(
                    f"[LENA] engine.generate attempt={attempt+1}/{max_retries+1} model={current_model}"
                )

                result = self.engine.generate(messages, model=current_model)
                
                content = result.get("content", "").strip()
                usage = result.get("usage", {})
                finish_reason = result.get("finish_reason", "stop")

                if not content:
                    self.logger.warning(f"[LENA] Empty content from model={current_model}")
                    content = "Response generated but content is empty."

                if not isinstance(content, str):
                    content = str(content)

                response_preview = content[:100].replace('\n', ' ')
                self.logger.info(
                    f"[LENA] Success model={current_model} len={len(content)} "
                    f"preview='{response_preview}...'"
                )

                return {
                    "choices": [{
                        "message": {"role": "assistant", "content": content},
                        "finish_reason": finish_reason,
                        "index": 0
                    }],
                    "usage": usage,
                    "model": current_model,
                }

            except Exception as exc:
                self.logger.error(
                    f"[LENA] Engine failed attempt={attempt+1}/{max_retries+1} "
                    f"model={current_model} error={type(exc).__name__}: {exc}",
                    exc_info=True
                )

                if attempt >= max_retries:
                    self.logger.error(
                        f"[LENA] All retries exhausted for model={current_model}"
                    )
                    return {
                        "choices": [{
                            "message": {"role": "assistant", "content": 
                                "Desculpe, não consegui gerar uma resposta no momento. "
                                "Por favor, tente novamente ou use um modelo diferente."
                            },
                            "finish_reason": "error",
                            "index": 0
                        }],
                        "model": current_model,
                    }

                sleep_time = 0.5 * (2 ** attempt)
                self.logger.info(f"[LENA] Retrying sleep={sleep_time}s")
                time.sleep(sleep_time)

                if current_model != self.default_model:
                    current_model = self.default_model
                    self.logger.info(f"[LENA] Fallback to default model={current_model}")
                else:
                    available = list(ModelRegistry.keys())
                    if "phi3" in available:
                        current_model = "phi3"
                    elif available:
                        current_model = available[0]
                    self.logger.info(f"[LENA] Fallback to model={current_model}")

        self.logger.error("[LENA] Unexpected exit from execute_model")
        return {
            "choices": [{
                "message": {"role": "assistant", "content": 
                    "Erro inesperado ao gerar resposta. Por favor, tente novamente."
                },
                "finish_reason": "error",
                "index": 0
            }],
            "model": current_model,
        }

    def post_process(self, response: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Post-process response to ensure OpenAI format."""
        full_response = {
            "id": f"chatcmpl-{uuid.uuid4().hex}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": response.get("choices", [{"message": {"content": ""}, "finish_reason": "stop"}]),
            "usage": response.get("usage", {})
        }
        
        for choice in full_response["choices"]:
            if "message" not in choice:
                choice["message"] = {"content": ""}
            if "finish_reason" not in choice:
                choice["finish_reason"] = "stop"
            if "index" not in choice:
                choice["index"] = 0
            
            if isinstance(choice["message"].get("content"), (dict, list)):
                choice["message"]["content"] = str(choice["message"]["content"])
        
        return full_response

    def _manage_cache(self, cache_key: str) -> None:
        """Manage cache size with FIFO eviction."""
        if cache_key not in self.cache_keys_order:
            self.cache_keys_order.append(cache_key)
        
        if len(self.response_cache) > self.max_cache_size:
            if self.cache_keys_order:
                oldest_key = self.cache_keys_order.popleft()
                if oldest_key in self.response_cache:
                    del self.response_cache[oldest_key]
                    self.logger.debug(
                        f"Evicted cache entry (FIFO): {oldest_key[:8]}... "
                        f"(cache size: {len(self.response_cache)}/{self.max_cache_size})"
                    )

    def run(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Main run method - synchronous for compatibility."""
        start_time = time.time()
        try:
            valid_messages = self.validate_messages(messages)
            if not valid_messages:
                elapsed = time.time() - start_time
                self.logger.warning(f"Invalid input processed in {elapsed:.2f}s")
                return self.post_process(
                    {
                        "choices": [
                            {
                                "message": {
                                    "content": "Desculpe, a entrada fornecida é inválida. "
                                               "Por favor, verifique o formato das mensagens."
                                }
                            }
                        ]
                    },
                    self.default_model
                )
            
            self.update_memory(valid_messages)

            session_id = "default"
            if session_id not in self.sessions:
                self.sessions[session_id] = []
            self.sessions[session_id].extend(valid_messages)
            history = self.sessions[session_id][-10:]

            context = self.build_context(history)
            
            query = ""
            for m in reversed(valid_messages):
                if m.get("role") == "user" and m.get("content"):
                    query = m["content"]
                    break

            route = self.route_query(query)

            if route == "local":
                self.logger.info(f"[LENA] Local command detected: {query}")
                return self.handle_local_command(query)
            
            if not query:
                elapsed = time.time() - start_time
                self.logger.warning(f"No user query found, processed in {elapsed:.2f}s")
                return self.post_process(
                    {
                        "choices": [
                            {
                                "message": {
                                    "content": "Não consegui encontrar uma consulta de usuário "
                                               "nas mensagens fornecidas."
                                }
                            }
                        ]
                    },
                    self.default_model
                )
            
            cache_key = self._generate_cache_key(query)
            if cache_key in self.response_cache:
                elapsed = time.time() - start_time
                self.logger.info(
                    f"[LENA] Cache HIT | "
                    f"key={cache_key[:8]}... | "
                    f"query='{query[:50]}...' | "
                    f"elapsed={elapsed:.2f}s"
                )
                return self.response_cache[cache_key]
            
            tool_name = self.detect_tool_intent(query)
            if tool_name:
                self.logger.info(f"[LENA] Tool detected: {tool_name} for query '{query[:50]}...'")
                try:
                    tool_result = self.execute_tool(tool_name, {"query": query})
                    response_content = f"Tool result: {tool_result}"
                except Exception as tool_exc:
                    self.logger.error(f"[LENA] Tool execution failed: {tool_exc}", exc_info=True)
                    response_content = (
                        f"Desculpe, não consegui executar a ferramenta '{tool_name}'. "
                        f"Erro: {str(tool_exc)}"
                    )
                
                full_response = self.post_process({
                    "choices": [{"message": {"content": response_content}}]
                }, self.default_model)
                self._manage_cache(cache_key)
                self.response_cache[cache_key] = full_response
                self.update_memory([{"role": "assistant", "content": response_content}])
                elapsed = time.time() - start_time
                self.logger.info(f"[LENA] Tool response generated in {elapsed:.2f}s for {tool_name}")
                return full_response
            
            selected_model = self.select_model(context, query)
            
            response = self.execute_model(selected_model, context)
            
            full_response = self.post_process(response, selected_model)
            
            self._manage_cache(cache_key)
            self.response_cache[cache_key] = full_response
            
            assistant_content = full_response.get("choices", [{}])[0].get("message", {}).get("content", "")
            if assistant_content:
                assistant_msg = {
                    "role": "assistant", 
                    "content": assistant_content
                }
                self.update_memory([assistant_msg])
            
            elapsed = time.time() - start_time
            self.logger.info(
                f"[LENA] Response complete | "
                f"model={selected_model} | "
                f"elapsed={elapsed:.2f}s | "
                f"query='{query[:50]}...'"
            )
            
            return full_response
            
        except Exception as exc:
            elapsed = time.time() - start_time
            self.logger.error(
                f"[LENA] Agent run failed after {elapsed:.2f}s: {exc}",
                exc_info=True
            )
            return self.post_process(
                {
                    "choices": [
                        {
                            "message": {
                                "content": "Desculpe, ocorreu um erro ao processar sua solicitação. "
                                           "Por favor, tente novamente."
                            }
                        }
                    ]
                },
                self.default_model
            )

    async def run_stream_async(self, messages: List[Dict[str, Any]]):
        """Async generator for real streaming responses using engine.stream()."""
        try:
            valid_messages = self.validate_messages(messages)
            if not valid_messages:
                yield self._create_stream_chunk("Desculpe, a entrada fornecida é inválida.")
                return

            self.update_memory(valid_messages)
            context = self.build_context(valid_messages)

            query = ""
            for m in reversed(valid_messages):
                if m.get("role") == "user" and m.get("content"):
                    query = m["content"]
                    break

            if not query:
                yield self._create_stream_chunk("Não consegui encontrar uma consulta de usuário.")
                return

            selected_model = self.select_model(context, query)

            messages_engine = [
                Message(
                    role=_to_role(m.get("role", "user")),
                    content=str(m.get("content", ""))
                )
                for m in context
            ]

            self.logger.info(
                f"[LENA] Stream start model={selected_model} messages={len(messages_engine)}"
            )

            full_content = ""
            try:
                async for token in self.engine.stream(
                    messages_engine, 
                    model=selected_model
                ):
                    if token:
                        full_content += token
                        yield self._create_stream_chunk(token)

                yield self._create_stream_chunk_end()

            except Exception as stream_exc:
                self.logger.error(
                    f"[LENA] Stream generation failed: {stream_exc}",
                    exc_info=True
                )
                yield self._create_stream_chunk(
                    f" [Erro ao processar: {str(stream_exc)[:50]}]"
                )
                yield self._create_stream_chunk_end()
                return

            if full_content:
                self.logger.info(
                    f"[LENA] Stream complete model={selected_model} "
                    f"total_tokens={len(full_content)//4}"
                )
                self.update_memory([{"role": "assistant", "content": full_content}])

        except Exception as exc:
            self.logger.error(f"[LENA] Stream error: {exc}", exc_info=True)
            yield self._create_stream_chunk("Erro ao processar stream.")
            yield self._create_stream_chunk_end()

    def run_stream(self, messages: List[Dict[str, Any]]):
        """Generator wrapper for async streaming - returns synchronous generator."""
        async def async_stream():
            async for chunk in self.run_stream_async(messages):
                yield chunk

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        gen = async_stream()
        try:
            while True:
                try:
                    chunk = loop.run_until_complete(gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
        finally:
            loop.close()

    def _create_stream_chunk(self, text: str) -> str:
        """Create a streaming chunk in SSE format."""
        chunk = {
            "id": f"chatcmpl-{uuid.uuid4().hex}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": self.default_model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": text},
                    "finish_reason": None
                }
            ]
        }
        return f"data: {json.dumps(chunk)}\n\n"

    def _create_stream_chunk_end(self) -> str:
        """Create final streaming chunk signaling completion."""
        chunk = {
            "id": f"chatcmpl-{uuid.uuid4().hex}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": self.default_model,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }
            ]
        }
        return f"data: {json.dumps(chunk)}\n\n"