from __future__ import annotations

import random

from openjarvis.lena.social_state import LenaSocialState


class LenaConversationalizer:
    OPENERS = ["hm, ", "olha, ", "então, ", "é... ", "pois é, ", "", ""]
    EMOTIONAL_OPENERS = ["hm. ", "poxa... ", "é... ", ""]

    FOLLOWUPS = [
        " quer me contar melhor?",
        " isso já vem acumulando?",
        " tô te ouvindo.",
        "",
        "",
    ]

    @classmethod
    def humanize(cls, text: str, social_state: LenaSocialState, user_text: str) -> str:
        if not text:
            return text

        text = cls._normalize(text)
        text = cls._inject_opener(text, social_state)
        text = cls._inject_followup(text, user_text)
        text = cls._soft_imperfection(text)
        return text.strip()

    @classmethod
    def _normalize(cls, text: str) -> str:
        banned = ["😊", "😉", "😥", "🤔", "💪", "☕", "gata", "sussa"]
        for b in banned:
            text = text.replace(b, "")
        return " ".join(text.strip().split())

    @classmethod
    def _inject_opener(cls, text: str, social_state: LenaSocialState) -> str:
        if len(text.split()) < 6:
            return text

        lowered = text.lower()
        if lowered.startswith(("hm", "olha", "então", "é...", "pois é", "entendo")):
            return text

        if social_state.emotional_tension >= 1:
            return random.choice(cls.EMOTIONAL_OPENERS) + text

        return random.choice(cls.OPENERS) + text

    @classmethod
    def _inject_followup(cls, text: str, user_text: str) -> str:
        lowered = user_text.lower()

        emotional = any(
            x in lowered
            for x in ("cansado", "exausto", "mal", "triste", "ansioso", "sobrecarregado")
        )

        if emotional and "?" not in text and len(text.split()) < 26:
            text += random.choice(cls.FOLLOWUPS)

        return text

    @classmethod
    def _soft_imperfection(cls, text: str) -> str:
        text = text.replace("E aí!", "")
        text = text.replace("Tudo sussa!", "")
        text = text.replace("Que tal um cafézinho pra dar um up no dia?", "")
        text = text.replace("  ", " ")
        return text.strip(" ,")
