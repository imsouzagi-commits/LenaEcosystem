from __future__ import annotations


class LenaResponseNaturalizer:
    def __init__(self) -> None:
        pass

    def available(self) -> bool:
        return False

    def should_naturalize(self, text: str) -> bool:
        return False

    def naturalize(self, question: str, raw_answer: str) -> str:
        return raw_answer
