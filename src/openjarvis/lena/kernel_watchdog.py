from __future__ import annotations

import threading
from openjarvis.lena.thread_guard import run_guarded_background
from typing import Any

from openjarvis.lena.boot_logger import LenaBootLogger
from openjarvis.lena.page_bridge import LenaPageBridge


class LenaKernelWatchdog:
    def __init__(
        self,
        kernel: Any,
        shutdown_event: threading.Event | None = None,
        interval_seconds: float = 5.0,
    ) -> None:
        self.kernel = kernel
        self.shutdown_event = shutdown_event or threading.Event()
        self.interval_seconds = interval_seconds
        self._thread: threading.Thread | None = None
        self._lock = threading.RLock()

    def start(self) -> None:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return

            self._thread = threading.Thread(
                target=self._run,
                name="lena-kernel-watchdog",
                daemon=True,
            )
            self._thread.start()

    def stop(self, timeout: float = 2.0) -> None:
        self.shutdown_event.set()
        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=timeout)

    def _run(self) -> None:
        while not self.shutdown_event.is_set():
            try:
                self.kernel._refresh_health()
                self._publish_page_snapshot()
            except Exception as exc:
                self.kernel.state.push_notification(f"watchdog_error:{exc}")
                LenaBootLogger.write(f"watchdog error: {exc}")

            self.shutdown_event.wait(self.interval_seconds)

    def _publish_page_snapshot(self) -> None:
        snapshot = self.kernel.state.snapshot()
        health = snapshot["health_status"]
        workspace_index = self.kernel.registry.get("workspace_index")
        workspace_index_size = len(workspace_index) if isinstance(workspace_index, dict) else 0

        try:
            LenaPageBridge.publish(
                {
                    "initialized": snapshot["initialized"],
                    "active_jobs": len(snapshot["active_jobs"]),
                    "queued_notifications": len(snapshot["queued_notifications"]),
                    "workspace_index_status": snapshot["workspace_index_status"],
                    "workspace_index_size": workspace_index_size,
                    "health": {
                        "cpu": health.cpu_percent,
                        "memory": health.memory_percent,
                        "uptime": health.process_uptime_seconds,
                    },
                }
            )
        except Exception as exc:
            self.kernel.state.push_notification(f"page_bridge_error:{exc}")
            LenaBootLogger.write(f"page bridge publish error: {exc}")

    @classmethod
    def start_for_kernel(cls, kernel: Any) -> "LenaKernelWatchdog":
        watchdog = cls(kernel, getattr(kernel, "shutdown_event", None))
        watchdog.start()
        return watchdog
