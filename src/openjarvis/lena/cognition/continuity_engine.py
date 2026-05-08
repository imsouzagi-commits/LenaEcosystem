from __future__ import annotations


class LenaContinuityEngine:

    @classmethod
    def stage(
        cls,
        recurrence: int,
        open_loops: int,
        continuity_flag: bool,
    ) -> int:

        score = 0

        if continuity_flag:
            score += 2

        score += min(3, recurrence)
        score += min(3, open_loops)

        return min(9, max(4, score + 4))
