from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LenaIntentionState:
    open_intentions: list[dict[str, Any]] = field(default_factory=list)
