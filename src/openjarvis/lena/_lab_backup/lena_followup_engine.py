from __future__ import annotations

import random


class LenaFollowupEngine:
    FATIGUE = [
        "isso vem de alguns dias?",
        "você já acordou assim?",
        "aconteceu algo hoje ou é acúmulo?",
    ]

    UNCERTAINTY = [
        "tem alguma decisão te travando?",
        "é excesso de coisa na cabeça?",
        "você sente que não consegue organizar pensamento?",
    ]

    BURNOUT = [
        "você sente mais cansaço ou mais confusão?",
        "isso tá ficando constante essa semana?",
        "sua cabeça não desliga nem quando para?",
    ]

    DISTRESS = [
        "tem algo te pressionando mais forte hoje?",
        "isso piorou nas últimas horas?",
    ]

    @classmethod
    def extend(cls, user_text: str, response: str, route: str, memory) -> str:
        if route not in {"EMOTIONAL_CHECK", "GREETING", "SOCIAL_CHAT", "LLM_FALLBACK"}:
            return response

        if "?" in response:
            return response

        social = memory.social_state
        profile = memory.preview_psychological_profile(user_text)

        if social.emotional_direction == "stuck" and "burnout_cognitive" in profile:
            return response + " " + random.choice(cls.BURNOUT)

        if "burnout_cognitive" in profile:
            return response + " " + random.choice(cls.BURNOUT)

        if "fatigue_loop" in profile and "uncertainty_loop" in profile:
            return response + " " + random.choice(cls.BURNOUT)

        if "fatigue_loop" in profile:
            return response + " " + random.choice(cls.FATIGUE)

        if "uncertainty_loop" in profile:
            return response + " " + random.choice(cls.UNCERTAINTY)

        if "distress_cycle" in profile:
            return response + " " + random.choice(cls.DISTRESS)

        return response
