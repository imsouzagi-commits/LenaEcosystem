# src/openjarvis/intelligence/phonetic_resolver.py

from __future__ import annotations

import difflib
import re
import unicodedata
from typing import Dict, Optional


class PhoneticResolver:
    def __init__(self):
        self.verb_aliases = {
            "abre": [
                "abre", "abrir", "abri", "abris", "abrisa", "abresa",
                "abreça", "abriço", "open", "launch"
            ],
            "fecha": [
                "fecha", "fechar", "fecham", "feicha", "ficha",
                "feixa", "quit", "close"
            ],
            "liga": [
                "liga", "ligar", "ative", "ativa"
            ],
            "desliga": [
                "desliga", "desliga", "desative", "desativa"
            ],
            "aumenta": [
                "aumenta", "aumentar", "sobe", "sube"
            ],
            "abaixa": [
                "abaixa", "abaixar", "desce", "diminuir"
            ],
        }

    def strip_accents(self, text: str) -> str:
        return "".join(
            c for c in unicodedata.normalize("NFD", text)
            if unicodedata.category(c) != "Mn"
        )

    def clean(self, text: str) -> str:
        text = self.strip_accents(text.lower())
        text = re.sub(r"[^\w\s]", " ", text)
        return " ".join(text.split())

    def strip_wakeword(self, text: str) -> str:
        q = self.clean(text)

        wake_variants = [
            "lena", "le na", "leina", "lenda", "leana",
            "lenaah", "lenna", "lenaa", "le ena"
        ]

        for wake in wake_variants:
            q = q.replace(wake, "")

        return " ".join(q.split())

    def resolve_action(self, text: str) -> str:
        q = self.clean(text)

        best_action = "unknown"
        best_score = 0.0

        for canonical, aliases in self.verb_aliases.items():
            for alias in aliases:
                score = difflib.SequenceMatcher(None, q, alias).ratio()
                if score > best_score:
                    best_score = score
                    best_action = canonical

        if best_score >= 0.55:
            return best_action

        words = q.split()
        for word in words:
            for canonical, aliases in self.verb_aliases.items():
                for alias in aliases:
                    score = difflib.SequenceMatcher(None, word, alias).ratio()
                    if score > 0.68:
                        return canonical

        return "unknown"

    def resolve_target(self, text: str, app_map: Dict[str, str]) -> Optional[str]:
        q = self.clean(text)

        best_key = None
        best_score = 0.0

        joined_apps = list(app_map.keys())

        for app in joined_apps:
            score = difflib.SequenceMatcher(None, q, app).ratio()
            if score > best_score:
                best_score = score
                best_key = app

        words = q.split()
        for word in words:
            for app in joined_apps:
                score = difflib.SequenceMatcher(None, word, app).ratio()
                if score > best_score:
                    best_score = score
                    best_key = app

            if best_score >= 0.50 and best_key is not None:
                return app_map[best_key]

        return None