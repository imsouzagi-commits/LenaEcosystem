from __future__ import annotations

from typing import TypedDict


class ContinuityPayload(TypedDict):
    topic: str | None
    recurrence: int
    stage: int
    arc: str
    response_pressure: int


class LenaContinuityEngine:
    @staticmethod
    def resolve(memory, topic: str | None) -> ContinuityPayload:
        social = memory.social_state

        if not topic:
            return {
                "topic": None,
                "recurrence": 0,
                "stage": 0,
                "arc": social.current_conversation_arc,
                "response_pressure": social.presence_momentum,
            }

        recurrence = int(memory.recent_topic_windows.get(topic, 0))
        unresolved = int(social.unresolved_loops)
        depth = int(social.conversation_depth)

        confidence = recurrence + unresolved + depth

        if confidence < 3:
            stage = 0
            topic = None
        else:
            stage = min(4, max(1, recurrence // 2 + unresolved // 2 + depth // 3))

        pressure = min(
            10,
            recurrence
            + unresolved
            + social.emotional_gravity
            + social.presence_momentum,
        )

        return {
            "topic": topic,
            "recurrence": recurrence,
            "stage": stage,
            "arc": social.current_conversation_arc,
            "response_pressure": pressure,
        }
