from __future__ import annotations

import random

from openjarvis.lena.narrative_tension_engine import LenaNarrativeTensionEngine
from openjarvis.lena.intention_recall_engine import LenaIntentionRecallEngine


class LenaAutonomousCuriosityEngine:
    @classmethod
    def render_fragment(cls, memory, user_text: str, topic: str) -> str | None:
        social = memory.social_state

        if social.presence_momentum < 1:
            return None

        if social.unresolved_loops < 2:
            return None

        if not LenaNarrativeTensionEngine.has_live_tension(memory):
            return None

        latest_intention = LenaIntentionRecallEngine.latest_open_intention(memory)
        short_user = len(user_text.split()) <= 4

        if short_user and latest_intention and random.random() < 0.45:
            return random.choice([
                "você encurtou bem na parte em que isso toca.",
                "você reduziu justo onde parecia ter mais coisa.",
                "a parte central ainda parece meio contornada.",
            ])

        if latest_intention and random.random() < 0.30:
            return random.choice([
                "tem um ponto aqui que ainda não saiu inteiro.",
                "acho que ainda tem uma camada por baixo disso.",
            ])

        return None
