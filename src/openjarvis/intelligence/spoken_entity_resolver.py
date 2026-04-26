from __future__ import annotations

from typing import Dict, Optional

from openjarvis.intelligence.brazilian_phonetic_engine import BrazilianPhoneticEngine


class SpokenEntityResolver:
    def __init__(self):
        self.engine = BrazilianPhoneticEngine()

    def resolve_entity(self, text: str, candidates: Dict[str, str]) -> Optional[str]:
        return self.engine.resolve(text, candidates)