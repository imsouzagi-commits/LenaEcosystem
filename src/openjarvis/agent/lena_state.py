from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LenaState:
    user_name: Optional[str] = None
    user_mood: Optional[str] = None
    conversation_mode: str = "neutral"
    relationship_warmth: float = 0.35
    last_topics: List[str] = field(default_factory=list)

    def register_topic(self, topic: str) -> None:
        if not topic:
            return

        self.last_topics.append(topic)

        if len(self.last_topics) > 8:
            self.last_topics = self.last_topics[-8:]

    def increase_warmth(self, amount: float = 0.05) -> None:
        self.relationship_warmth = min(1.0, self.relationship_warmth + amount)

    def decrease_warmth(self, amount: float = 0.03) -> None:
        self.relationship_warmth = max(0.0, self.relationship_warmth - amount)