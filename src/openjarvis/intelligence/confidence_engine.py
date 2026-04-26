from __future__ import annotations


class ConfidenceEngine:
    def score(
        self,
        intent: str,
        domain: str,
        target: str,
        resolved: bool,
        raw_text: str,
    ) -> float:
        score = 0.0

        if intent != "unknown":
            score += 0.30

        if domain != "unknown":
            score += 0.20

        if target:
            score += 0.20

        if resolved:
            score += 0.20

        if len(raw_text.split()) >= 2:
            score += 0.10

        return min(score, 1.0)