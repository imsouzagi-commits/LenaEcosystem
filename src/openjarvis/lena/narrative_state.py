from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LenaNarrativeState:
    unresolved_user_threads: list[dict] = field(default_factory=list)
    assistant_open_loops: list[dict] = field(default_factory=list)
    suspended_topics: list[str] = field(default_factory=list)
    last_unresolved_ts: float = 0.0
