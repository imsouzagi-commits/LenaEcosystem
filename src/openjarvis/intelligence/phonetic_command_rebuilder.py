from __future__ import annotations

import difflib
import re
import unicodedata
from typing import Dict, List


def _ascii(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c)).lower()


class PhoneticCommandRebuilder:
    def __init__(self, installed_apps: Dict[str, str]):
        self.installed_apps = installed_apps

        self.wakewords = [
            "lena", "lina", "le na", "lenda", "leena", "leina", "lela"
        ]

        self.stopwords = {
            "o", "os", "a", "as", "de", "do", "da", "e", "para"
        }

        self.intent_aliases = {
            "open": [
                "abre", "abreo", "abro", "abru", "abri", "abriga",
                "abris", "abrisa", "abrico", "abrir"
            ],
            "close": [
                "fecha", "fechar", "feche", "fexa", "fecham", "fechao"
            ],
            "up": [
                "aumenta", "sobe", "mais", "alto"
            ],
            "down": [
                "abaixa", "desce", "menos"
            ],
        }

        self.system_targets = [
            "spotify",
            "safari",
            "whatsapp",
            "finder",
            "wifi",
            "bluetooth",
            "volume",
            "brilho",
        ] + list(installed_apps.keys())

    def strip_wakeword(self, text: str) -> str:
        q = _ascii(text)

        for wake in self.wakewords:
            q = q.replace(wake, " ")

        q = re.sub(r"\s+", " ", q)
        return q.strip()

    def _best_match(self, token: str, candidates: List[str], cutoff: float) -> str | None:
        matches = difflib.get_close_matches(token, candidates, n=1, cutoff=cutoff)
        return matches[0] if matches else None

    def detect_intent(self, tokens: List[str]) -> tuple[str | None, List[str]]:
        alias_map = {}
        for intent, words in self.intent_aliases.items():
            for word in words:
                alias_map[word] = intent

        for idx, token in enumerate(tokens):
            best = self._best_match(token, list(alias_map.keys()), cutoff=0.50)
            if best:
                return alias_map[best], tokens[idx + 1 :]

        return None, tokens

    def detect_target(self, tokens: List[str]) -> str | None:
        filtered = [t for t in tokens if t not in self.stopwords]

        if not filtered:
            return None

        joined = " ".join(filtered)

        best_joined = self._best_match(joined, self.system_targets, cutoff=0.40)
        if best_joined:
            return self.installed_apps.get(best_joined, best_joined.title())

        for token in filtered:
            best = self._best_match(token, self.system_targets, cutoff=0.40)
            if best:
                return self.installed_apps.get(best, best.title())

        return None

    def rebuild(self, text: str) -> str:
        cleaned = self.strip_wakeword(text)
        tokens = cleaned.split()

        if not tokens:
            return cleaned

        intent, remaining_tokens = self.detect_intent(tokens)
        target = self.detect_target(remaining_tokens)

        if intent and target:
            if intent == "open":
                return f"abre {target.lower()}"
            if intent == "close":
                return f"fecha {target.lower()}"
            if intent == "up":
                return f"aumenta {target.lower()}"
            if intent == "down":
                return f"abaixa {target.lower()}"

        return cleaned