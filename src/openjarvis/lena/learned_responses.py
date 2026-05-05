from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class LenaLearnedResponses:
    FILE_PATH = Path(__file__).resolve().parent / "learning_bank" / "responses.json"

    @classmethod
    def load(cls) -> Dict[str, List[str]]:
        if not cls.FILE_PATH.exists():
            return {
                "fatigue": [],
                "uncertainty": [],
                "distress": [],
            }

        try:
            with open(cls.FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError("invalid learned responses")

            return {
                "fatigue": list(data.get("fatigue", [])),
                "uncertainty": list(data.get("uncertainty", [])),
                "distress": list(data.get("distress", [])),
            }
        except Exception:
            return {
                "fatigue": [],
                "uncertainty": [],
                "distress": [],
            }

    @classmethod
    def save(cls, payload: Dict[str, List[str]]) -> None:
        cls.FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

        normalized = {
            "fatigue": sorted(set(payload.get("fatigue", []))),
            "uncertainty": sorted(set(payload.get("uncertainty", []))),
            "distress": sorted(set(payload.get("distress", []))),
        }

        with open(cls.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(normalized, f, ensure_ascii=False, indent=2)

    @classmethod
    def add_responses(cls, topic: str, responses: List[str]) -> None:
        if topic not in {"fatigue", "uncertainty", "distress"}:
            return

        bank = cls.load()
        current = set(bank.get(topic, []))

        for item in responses:
            cleaned = str(item).strip()
            if len(cleaned) >= 6:
                current.add(cleaned)

        bank[topic] = sorted(current)
        cls.save(bank)
