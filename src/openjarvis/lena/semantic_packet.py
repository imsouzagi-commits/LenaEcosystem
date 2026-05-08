from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class LenaSemanticPacket:
    primary_topic: str
    primary_shade: str | None = None
    secondary_topic: str | None = None
    latent_topic: str | None = None

    raw_scores: dict[str, float] = field(default_factory=dict)
    matched_roots: list[tuple[str, str]] = field(default_factory=list)

    continuation_flag: bool = False
    recurrence: int = 0
    continuity_stage: int = 0
    response_pressure: float = 4.0
    memory_resonance: float = 0.0

    mode: str = "mirror"
    stance: str = "observe"

    echo_snippets: list[str] = field(default_factory=list)
    echo_responses: list[str] = field(default_factory=list)
    familiarity_density: int = 0
    session_hits: int = 0

    @property
    def topic_spread(self) -> int:
        return len([x for x in (self.primary_topic, self.secondary_topic, self.latent_topic) if x])
