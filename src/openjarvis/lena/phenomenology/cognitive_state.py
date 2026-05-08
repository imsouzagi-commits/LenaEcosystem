from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CognitiveState:

    active_topic: str | None = None

    active_shade: str | None = None

    cognitive_charge: float = 0.0

    semantic_inertia: float = 0.0

    drift_tendency: float = 0.0

    emotional_residue: float = 0.0

    continuity_residue: float = 0.0

    silence_accumulation: float = 0.0

    last_mode: str | None = None

    turn_index: int = 0

    def decay(self) -> None:

        self.cognitive_charge *= 0.82

        self.semantic_inertia *= 0.88

        self.drift_tendency *= 0.84

        self.emotional_residue *= 0.90

        self.continuity_residue *= 0.86

        self.silence_accumulation *= 0.76

    def ingest(
        self,
        topic: str,
        shade: str | None,
        pressure: float,
        continuity: float,
        resonance: float,
        mode: str,
    ) -> None:

        self.turn_index += 1

        if self.active_topic == topic:
            self.semantic_inertia += 1.4
        else:
            self.drift_tendency += 0.9

        self.active_topic = topic

        self.active_shade = shade

        self.cognitive_charge += (
            pressure * 0.42
        )

        self.emotional_residue += (
            resonance * 0.33
        )

        self.continuity_residue += (
            continuity * 0.58
        )

        self.semantic_inertia = min(
            10.0,
            self.semantic_inertia,
        )

        self.cognitive_charge = min(
            10.0,
            self.cognitive_charge,
        )

        self.emotional_residue = min(
            10.0,
            self.emotional_residue,
        )

        self.continuity_residue = min(
            10.0,
            self.continuity_residue,
        )

        self.last_mode = mode
