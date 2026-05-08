from __future__ import annotations


class LenaResponsePressureEngine:

    MIN_PRESSURE = 4.0
    MAX_PRESSURE = 9.0

    @classmethod
    def compute(
        cls,
        semantic_spread: int,
        continuity_stage: int,
        recurrence: int,
        memory_resonance: float,
        question_pressure: bool,
        open_loops: int,
    ) -> float:

        pressure = 4.0

        pressure += min(1.2, semantic_spread * 0.45)
        pressure += min(1.0, continuity_stage * 0.35)
        pressure += min(0.8, recurrence * 0.2)
        pressure += min(0.8, memory_resonance * 0.15)
        pressure += min(0.8, open_loops * 0.2)

        if question_pressure:
            pressure += 0.55

        return max(
            cls.MIN_PRESSURE,
            min(cls.MAX_PRESSURE, round(pressure, 2))
        )
