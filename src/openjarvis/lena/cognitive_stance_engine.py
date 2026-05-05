from __future__ import annotations

import random


class LenaCognitiveStanceEngine:
    @staticmethod
    def decide(memory, topic: str, mode: str) -> str:
        social = memory.social_state
        history = memory.recent_semantic_responses(topic)

        last = history[-1].lower() if history else ""

        candidates: list[str] = []

        if mode == "mirror":
            candidates += ["observe", "locate"]

        if mode == "continuity":
            candidates += ["pattern_link", "observe", "locate"]

        if mode == "invite":
            candidates += ["probe", "locate", "pattern_link"]

        if mode == "contain":
            candidates += ["locate", "observe"]

        if mode == "deep_reflect":
            candidates += ["compress", "pattern_link", "probe"]

        if mode == "reflective_hold":
            candidates += ["compress", "locate"]

        if not candidates:
            candidates = ["observe"]

        filtered: list[str] = []

        for stance in candidates:
            if stance == "observe" and "parece" in last:
                continue
            if stance == "pattern_link" and "continua" in last:
                continue
            if stance == "compress" and "padr" in last:
                continue
            if stance == "probe" and "me " in last:
                continue
            filtered.append(stance)

        if filtered:
            candidates = filtered

        if social.unresolved_loops >= 6 and "compress" not in candidates and random.random() < 0.30:
            candidates.append("compress")

        if social.reflection_depth >= 5 and "pattern_link" not in candidates and random.random() < 0.25:
            candidates.append("pattern_link")

        return random.choice(candidates)
