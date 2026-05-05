from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from openjarvis.lena.workspace_center import LenaWorkspaceCenter


class LenaPersistentStore:
    AUDIT_FILE = LenaWorkspaceCenter.LOGS / "audit_log.jsonl"
    JOBS_FILE = LenaWorkspaceCenter.LOGS / "jobs_log.jsonl"
    BOOT_FILE = LenaWorkspaceCenter.LOGS / "boot_log.jsonl"

    @staticmethod
    def _append(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        enriched = {"ts": datetime.utcnow().isoformat(), **payload}

        with path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(enriched, ensure_ascii=False) + "\n")

    @classmethod
    def write_audit(cls, payload: dict[str, Any]) -> None:
        cls._append(cls.AUDIT_FILE, payload)

    @classmethod
    def write_job(cls, payload: dict[str, Any]) -> None:
        cls._append(cls.JOBS_FILE, payload)

    @classmethod
    def write_boot(cls, payload: dict[str, Any]) -> None:
        cls._append(cls.BOOT_FILE, payload)
