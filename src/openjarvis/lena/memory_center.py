from __future__ import annotations

import hashlib
import json
import time
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional


class MemoryCenter:
    def __init__(self, memory_path: Path):
        self.memory_path = memory_path

        self.short_term = deque(maxlen=100)
        self.long_term: List[Dict[str, Any]] = []
        self.sacred_memory: List[Dict[str, Any]] = []

        self.user_profile: Dict[str, List[str]] = {
            "likes": [],
            "appointments": [],
            "identity": [],
            "routine": [],
            "work": [],
        }

        self.response_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_order = deque(maxlen=150)
        self.cache_timestamps: Dict[str, float] = {}
        self.max_cache_size = 150
        self.cache_ttl_seconds = 1800

        self._load()

    def _load(self) -> None:
        if not self.memory_path.exists():
            return

        try:
            with open(self.memory_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, dict):
                self.long_term = data.get("long_term", [])
                self.sacred_memory = data.get("sacred_memory", [])
                self.user_profile = data.get("user_profile", self.user_profile)

            elif isinstance(data, list):
                self.long_term = data

        except Exception:
            self.long_term = []
            self.sacred_memory = []

    def save(self) -> None:
        try:
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)

            payload = {
                "long_term": self.long_term[-500:],
                "sacred_memory": self.sacred_memory[-120:],
                "user_profile": self.user_profile,
            }

            with open(self.memory_path, "w", encoding="utf-8") as file:
                json.dump(payload, file, indent=2, ensure_ascii=False)

        except Exception:
            pass

    def _normalize(self, text: str) -> str:
        return str(text or "").strip().lower()

    def _timestamp(self) -> float:
        return time.time()

    def _clean_memory_content(self, text: str) -> str:
        text = str(text or "").strip()

        removable_prefixes = [
            "registre que ",
            "registre ",
            "registro que ",
            "guarde que ",
            "guarde ",
            "salve que ",
            "salve ",
            "lembre que ",
            "lembre ",
        ]

        lowered = text.lower()

        for prefix in removable_prefixes:
            if lowered.startswith(prefix):
                text = text[len(prefix):].strip()
                break

        return text.strip(" .,!?:;")

    def should_store_long_term(self, content: str) -> bool:
        lowered = self._normalize(content)

        if not lowered:
            return False

        explicit_triggers = [
            "registre",
            "registro",
            "guarde",
            "salve",
            "lembre",
        ]

        spontaneous_patterns = [
            "meu nome é",
            "eu gosto de",
            "eu adoro",
            "eu prefiro",
            "prefiro",
            "eu trabalho",
            "eu sou",
            "amanhã tenho",
            "hoje tenho",
            "tenho consulta",
            "tenho reunião",
            "minha rotina",
            "costumo",
            "todo dia",
        ]

        return (
            any(x in lowered for x in explicit_triggers)
            or any(x in lowered for x in spontaneous_patterns)
        )

    def _memory_exists(self, content: str) -> bool:
        normalized = self._normalize(content)

        for item in self.long_term[-150:]:
            if self._normalize(item.get("content", "")) == normalized:
                return True

        return False

    def update(self, messages: List[Dict[str, Any]]) -> None:
        changed = False

        for msg in messages:
            self.short_term.append(msg)

            if msg.get("role") != "user":
                continue

            raw_content = str(msg.get("content", "")).strip()
            if not self.should_store_long_term(raw_content):
                continue

            content = self._clean_memory_content(raw_content)
            if not content:
                continue

            if self._memory_exists(content):
                continue

            record = {
                "role": "user",
                "content": content,
                "timestamp": self._timestamp(),
                "score": self._estimate_memory_score(content),
            }

            self.long_term.append(record)
            self._register_sacred_internal(content)
            self.classify_profile_memory(content)
            changed = True

        if changed:
            self._trim_memories()
            self.save()

    def _estimate_memory_score(self, content: str) -> int:
        lowered = self._normalize(content)
        score = 1

        if any(x in lowered for x in ["meu nome é", "eu sou"]):
            score += 5

        if any(x in lowered for x in ["amanhã tenho", "consulta", "reunião"]):
            score += 4

        if any(x in lowered for x in ["eu gosto de", "eu adoro", "eu prefiro"]):
            score += 3

        if any(x in lowered for x in ["eu trabalho", "empresa", "projeto"]):
            score += 2

        return score

    def _register_sacred_internal(self, content: str) -> None:
        lowered = self._normalize(content)

        sacred_patterns = [
            "meu nome é",
            "eu gosto de",
            "eu adoro",
            "eu prefiro",
            "amanhã tenho",
            "tenho consulta",
            "tenho reunião",
            "eu sou",
        ]

        if not any(x in lowered for x in sacred_patterns):
            return

        for item in self.sacred_memory:
            if self._normalize(item.get("content", "")) == lowered:
                return

        self.sacred_memory.append(
            {
                "content": content,
                "timestamp": self._timestamp(),
            }
        )

    def register_sacred(self, content: str) -> None:
        content = self._clean_memory_content(content)

        if not content:
            return

        if not self._memory_exists(content):
            self.long_term.append(
                {
                    "role": "user",
                    "content": content,
                    "timestamp": self._timestamp(),
                    "score": self._estimate_memory_score(content),
                }
            )

        self._register_sacred_internal(content)
        self.classify_profile_memory(content)
        self._trim_memories()
        self.save()

    def recall_sacred(self) -> List[str]:
        return [item["content"] for item in self.sacred_memory][-12:]

    def recall_long_term(self) -> List[str]:
        ranked = sorted(
            self.long_term,
            key=lambda x: (x.get("score", 0), x.get("timestamp", 0)),
            reverse=True,
        )
        return [item["content"] for item in ranked[:20]]

    def classify_profile_memory(self, content: str) -> None:
        lowered = self._normalize(content)

        if any(x in lowered for x in ["eu gosto de", "eu adoro", "eu prefiro", "prefiro"]):
            self._append_profile("likes", content)

        if any(x in lowered for x in ["amanhã tenho", "hoje tenho", "tenho consulta", "tenho reunião"]):
            self._append_profile("appointments", content)

        if any(x in lowered for x in ["meu nome é", "eu sou"]):
            self._append_profile("identity", content)

        if any(x in lowered for x in ["eu trabalho", "trabalho na", "sou desenvolvedor", "sou programador"]):
            self._append_profile("work", content)

        if any(x in lowered for x in ["minha rotina", "costumo", "todo dia"]):
            self._append_profile("routine", content)

    def _append_profile(self, key: str, content: str) -> None:
        normalized = self._normalize(content)

        for item in self.user_profile[key]:
            if self._normalize(item) == normalized:
                return

        self.user_profile[key].append(content)

    def _build_memory_summary_block(self) -> Optional[str]:
        blocks = []

        if self.user_profile["identity"]:
            blocks.append("Identidade: " + " | ".join(self.user_profile["identity"][-3:]))

        if self.user_profile["likes"]:
            blocks.append("Gostos: " + " | ".join(self.user_profile["likes"][-5:]))

        if self.user_profile["appointments"]:
            blocks.append("Compromissos: " + " | ".join(self.user_profile["appointments"][-5:]))

        if self.user_profile["work"]:
            blocks.append("Trabalho: " + " | ".join(self.user_profile["work"][-3:]))

        if self.user_profile["routine"]:
            blocks.append("Rotina: " + " | ".join(self.user_profile["routine"][-3:]))

        if not blocks:
            return None

        return "Memórias persistentes do usuário:\n" + "\n".join(blocks)

    def build_context(
        self,
        system_prompt: str,
        session_messages: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        enriched = [{"role": "system", "content": system_prompt}]

        memory_block = self._build_memory_summary_block()
        if memory_block:
            enriched.append({"role": "system", "content": memory_block})

        enriched.extend(session_messages[-12:])
        return enriched

    def _trim_memories(self) -> None:
        self.long_term = sorted(
            self.long_term,
            key=lambda x: (x.get("score", 0), x.get("timestamp", 0)),
            reverse=True,
        )[:500]

        self.sacred_memory = self.sacred_memory[-120:]

    def _memory_fingerprint(self) -> str:
        joined = "|".join([x.get("content", "") for x in self.long_term[-20:]])
        return hashlib.sha256(joined.encode()).hexdigest()[:8]

    def make_cache_key(self, query: str) -> str:
        base = self._normalize(query) + "|" + self._memory_fingerprint()
        return hashlib.sha256(base.encode()).hexdigest()[:16]

    def get_cache(self, key: str) -> Dict[str, Any] | None:
        if key not in self.response_cache:
            return None

        ts = self.cache_timestamps.get(key)
        if ts is None:
            return None

        if (time.time() - ts) > self.cache_ttl_seconds:
            self.response_cache.pop(key, None)
            self.cache_timestamps.pop(key, None)
            return None

        return self.response_cache[key]

    def set_cache(self, key: str, value: Dict[str, Any]) -> None:
        if key not in self.cache_order:
            self.cache_order.append(key)

        self.response_cache[key] = value
        self.cache_timestamps[key] = time.time()

        if len(self.response_cache) > self.max_cache_size:
            oldest = self.cache_order.popleft()
            self.response_cache.pop(oldest, None)
            self.cache_timestamps.pop(oldest, None)