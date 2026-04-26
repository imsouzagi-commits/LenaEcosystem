from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class UOCommand:
    raw_text: str
    intent: str
    domain: str
    target: str
    modifier: Optional[str] = None
    confidence: float = 0.0


@dataclass
class UOBatch:
    commands: List[UOCommand] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.commands) > 0