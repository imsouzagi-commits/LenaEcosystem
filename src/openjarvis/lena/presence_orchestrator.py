from __future__ import annotations

from openjarvis.lena.narrative_tension_engine import LenaNarrativeTensionEngine


class LenaPresenceOrchestrator:
    @staticmethod
    def decide(memory, semantic_mode: str) -> str:
        social = memory.social_state
        live_tension = LenaNarrativeTensionEngine.has_live_tension(memory)

        if semantic_mode == "memory_probe":
            return "memory"

        if semantic_mode == "social":
            return "engaged"

        if semantic_mode == "inquisitive":
            return "engaged"

        if semantic_mode == "narrative":
            if live_tension and social.unresolved_loops >= 2:
                return "reflective_hold"
            return "engaged"

        if semantic_mode != "emotional":
            return "engaged"

        if social.unresolved_loops >= 4:
            return "invite"

        if social.emotional_tension >= 2:
            return "continuity"

        return "mirror"
