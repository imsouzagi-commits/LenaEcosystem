from __future__ import annotations

from openjarvis.lena.social_engine import LenaSocialEngine


class LenaTurnManager:
    def __init__(self, memory_engine) -> None:
        self.memory_engine = memory_engine
        self.social_engine = LenaSocialEngine()

    def finalize_turn(self, user_text: str, raw_response: str) -> str:
        social_signal = self.social_engine.analyze(user_text)
        self._update_social_state(social_signal)
        self.memory_engine.push_exchange(user_text, raw_response)
        return raw_response

    def _update_social_state(self, social_signal: dict) -> None:
        state = self.memory_engine.social_state

        state.turns_count += 1

        if state.emotional_tension > 0:
            state.emotional_tension -= 1

        if social_signal.get("open_user"):
            state.intimacy_level += 1

        if social_signal.get("emotional"):
            state.warmth_level += 1
            state.emotional_tension += 1
