from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from openjarvis.lena.boot_logger import LenaBootLogger
from openjarvis.lena.workspace_center import LenaWorkspaceCenter


class LenaPageBridge:
    FILE = LenaWorkspaceCenter.DELIVERY / "lena_page_state.json"

    @classmethod
    def _atomic_write(cls, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")

        try:
            with tmp.open("w", encoding="utf-8") as file:
                file.write(content)
                file.flush()
                os.fsync(file.fileno())

            os.replace(tmp, path)
        finally:
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError as exc:
                    LenaBootLogger.write(f"page bridge tmp cleanup failed: {exc}")

    @classmethod
    def publish(cls, payload: dict[str, Any]) -> None:
        try:
            enriched = {
                "ts": datetime.utcnow().isoformat(),
                **payload,
            }
            content = json.dumps(enriched, ensure_ascii=False, indent=2)
            cls._atomic_write(cls.FILE, content)
        except Exception as exc:
            LenaBootLogger.write(f"page bridge publish failed: {exc}")

    @classmethod
    def snapshot(cls) -> dict[str, Any]:
        if not cls.FILE.exists():
            return {}

        try:
            data = json.loads(cls.FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception as exc:
            LenaBootLogger.write(f"page bridge snapshot failed: {exc}")
            return {}
