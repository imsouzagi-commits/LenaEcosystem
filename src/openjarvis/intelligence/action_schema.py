from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class ActionCommand:
    raw_text: str = ""
    normalized_text: str = ""
    intent: str = "unknown"
    domain: str = "unknown"
    target: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    is_compound: bool = False


@dataclass(slots=True)
class ActionBatch:
    commands: List[ActionCommand] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.commands) > 0