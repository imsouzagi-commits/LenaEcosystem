from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any

from openjarvis.lena.boot_logger import LenaBootLogger
from openjarvis.lena.workspace_center import LenaWorkspaceCenter


class LenaMemoryPersistence:
    SCHEMA_VERSION = 13

    FILE = LenaWorkspaceCenter.MEMORY / "memory_state.json"
    BACKUP_FILE = LenaWorkspaceCenter.MEMORY / "memory_state.lastgood.json"

    _lock = threading.RLock()

    @classmethod
    def default_payload(cls) -> dict[str, Any]:
        return {
            "schema_version": cls.SCHEMA_VERSION,
            "state": {},
            "history": [],
            "facts": {},
            "emotional_history": [],
            "topic_counters": {},
            "semantic_emotional_snippets": [],
            "psychological_signature": "stable",
            "psychological_profile": [],
            "episodic_events": [],
            "recent_topic_windows": {},
            "semantic_response_history": {},
            "exchange_significance": 0,
            "social_state": {},
            "narrative_state": {},
            "intention_state": {},
        }

    @classmethod
    def _normalize_payload(cls, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = cls.default_payload()
        normalized.update(payload)
        normalized["schema_version"] = cls.SCHEMA_VERSION

        dict_fields = (
            "state",
            "facts",
            "topic_counters",
            "recent_topic_windows",
            "semantic_response_history",
            "social_state",
            "narrative_state",
            "intention_state",
        )

        list_fields = (
            "history",
            "emotional_history",
            "semantic_emotional_snippets",
            "psychological_profile",
            "episodic_events",
        )

        for field in dict_fields:
            if not isinstance(normalized.get(field), dict):
                normalized[field] = {}

        for field in list_fields:
            if not isinstance(normalized.get(field), list):
                normalized[field] = []

        if not isinstance(normalized.get("exchange_significance"), int):
            try:
                normalized["exchange_significance"] = int(normalized.get("exchange_significance", 0))
            except Exception:
                normalized["exchange_significance"] = 0

        normalized["psychological_signature"] = str(normalized.get("psychological_signature", "stable"))
        return normalized

    @classmethod
    def _read_json(cls, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        if not isinstance(payload, dict):
            raise ValueError(f"memory payload is not an object: {path}")

        return payload

    @classmethod
    def _atomic_write_text(cls, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")

        try:
            with tmp_path.open("w", encoding="utf-8") as file:
                file.write(content)
                file.flush()
                os.fsync(file.fileno())
            os.replace(tmp_path, path)
        finally:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError as exc:
                    LenaBootLogger.write(f"memory tmp cleanup failed: {exc}")

    @classmethod
    def save(cls, payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            raise TypeError("memory payload must be a dict")

        with cls._lock:
            normalized = cls._normalize_payload(payload)
            content = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))

            try:
                cls._atomic_write_text(cls.FILE, content)
                cls._atomic_write_text(cls.BACKUP_FILE, content)
            except Exception as exc:
                LenaBootLogger.write(f"memory persistence save failed: {exc}")
                raise

    @classmethod
    def load(cls) -> dict[str, Any]:
        with cls._lock:
            if cls.FILE.exists():
                try:
                    return cls._normalize_payload(cls._read_json(cls.FILE))
                except Exception as exc:
                    LenaBootLogger.write(f"memory primary load failed: {exc}")

            if cls.BACKUP_FILE.exists():
                try:
                    return cls._normalize_payload(cls._read_json(cls.BACKUP_FILE))
                except Exception as exc:
                    LenaBootLogger.write(f"memory lastgood load failed: {exc}")

            LenaBootLogger.write("memory load returned default payload")
            return cls.default_payload()
