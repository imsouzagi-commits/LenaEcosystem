from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LenaSocialState:
    current_topic: str = "neutral"

    emotional_tension: int = 0
    emotional_gravity: int = 0
    emotional_direction: str = "stable"
    emotional_variability: int = 0
    last_emotion_topic: str = ""

    familiarity: int = 0
    trust_level: int = 0
    conversation_depth: int = 0

    turns_count: int = 0
    intimacy_level: int = 0
    reflection_depth: int = 0
    warmth_level: int = 0

    cognitive_load: int = 0
    continuity_score: int = 0

    openness_score: int = 0
    dependency_score: int = 0
    unresolved_loops: int = 0
    presence_momentum: int = 0

    last_response_mode: str = "minimal"
    current_conversation_arc: str = "idle"
    arc_stage: int = 0

    last_user_intent: str = ""
    last_assistant_mode: str = ""

    session_boot_id: int = 0
