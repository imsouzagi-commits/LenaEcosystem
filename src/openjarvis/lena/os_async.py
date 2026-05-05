from __future__ import annotations

import subprocess
import threading
from collections.abc import Callable

from openjarvis.lena.boot_logger import LenaBootLogger


class LenaOSAsync:
    @staticmethod
    def run(task: Callable[[], None]) -> None:
        def _runner() -> None:
            try:
                task()
            except Exception as exc:
                LenaBootLogger.write(f"os_async task failed: {exc}")

        threading.Thread(
            target=_runner,
            name="lena-os-async",
            daemon=True,
        ).start()

    @staticmethod
    def popen(args: list[str]) -> None:
        def _task() -> None:
            try:
                subprocess.Popen(
                    args,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as exc:
                LenaBootLogger.write(f"os_async popen failed {args}: {exc}")

        LenaOSAsync.run(_task)
