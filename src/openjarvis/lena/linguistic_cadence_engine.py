from __future__ import annotations

import random
from collections import Counter


class LenaLinguisticCadenceEngine:
    SATURATION_LIMIT = 3
    TRACK_WORDS = {
        "isso", "continua", "parece", "ainda", "dessa", "desse",
        "você", "voce", "fica", "ficou", "dentro", "aqui",
    }

    @staticmethod
    def _recent_words(memory) -> list[str]:
        words = []
        for bucket in memory.semantic_response_history.values():
            for text in bucket[-3:]:
                words.extend(text.lower().replace(".", "").replace(",", "").split())
        return words

    @classmethod
    def saturated_words(cls, memory) -> set[str]:
        counts = Counter(w for w in cls._recent_words(memory) if w in cls.TRACK_WORDS)
        return {w for w, n in counts.items() if n >= cls.SATURATION_LIMIT}

    @classmethod
    def clean_fragment(cls, memory, fragment: str) -> str:
        saturated = cls.saturated_words(memory)
        text = fragment

        replacements = {
            "isso": "essa coisa" if "isso" in saturated else "isso",
            "continua": "permanece" if "continua" in saturated else "continua",
            "parece": "soa" if "parece" in saturated else "parece",
            "ainda": "até agora" if "ainda" in saturated else "ainda",
        }

        for old, new in replacements.items():
            text = text.replace(old, new).replace(old.capitalize(), new.capitalize())

        return text

    @staticmethod
    def should_drop_optional() -> bool:
        return random.random() < 0.28

    @staticmethod
    def reorder(parts: list[str]) -> list[str]:
        if len(parts) <= 2:
            return parts

        if random.random() < 0.33:
            middle = parts[1:]
            random.shuffle(middle)
            return [parts[0]] + middle

        return parts

    @staticmethod
    def breathing_finish(text: str) -> str:
        if random.random() < 0.18:
            return text.replace(". ", ".  ")
        return text
