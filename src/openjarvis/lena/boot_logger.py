from __future__ import annotations

import threading
from datetime import datetime

from openjarvis.lena.workspace_center import LenaWorkspaceCenter


class LenaBootLogger:
    _lock = threading.RLock()
    _file = LenaWorkspaceCenter.LOGS / "lena_boot.log"

    @staticmethod
    def write(message: str) -> None:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[LENA BOOT {stamp}] {message}"
        print(line, flush=True)

        with LenaBootLogger._lock:
            try:
                LenaBootLogger._file.parent.mkdir(parents=True, exist_ok=True)
                with LenaBootLogger._file.open("a", encoding="utf-8") as file:
                    file.write(line + "\n")
            except Exception:
                pass
