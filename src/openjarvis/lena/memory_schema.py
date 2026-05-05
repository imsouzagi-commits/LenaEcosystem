from __future__ import annotations

from dataclasses import fields

from openjarvis.lena.social_state import LenaSocialState


class LenaMemorySchema:
    @staticmethod
    def normalize_social_state(payload: dict) -> LenaSocialState:
        raw = payload.get("social_state", {}) or {}

        valid_fields = {f.name for f in fields(LenaSocialState)}
        cleaned = {k: v for k, v in raw.items() if k in valid_fields}

        return LenaSocialState(**cleaned)

    @staticmethod
    def normalize_payload(payload: dict) -> dict:
        return {
            "state": payload.get("state", {}) or {},
            "history": payload.get("history", []) or [],
            "facts": payload.get("facts", {}) or {},
            "social_state": LenaMemorySchema.normalize_social_state(payload),
        }
