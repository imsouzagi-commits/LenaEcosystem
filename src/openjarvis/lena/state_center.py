from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List


@dataclass
class HealthStatus:
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    process_uptime_seconds: float = 0.0


@dataclass
class LenaGlobalState:
    MAX_NOTIFICATIONS: ClassVar[int] = 100

    initialized: bool = False
    boot_failure_reason: str = ""
    permission_status: dict = field(default_factory=dict)
    workspace_index_status: bool = False
    loaded_modules: Dict[str, object] = field(default_factory=dict)

    active_jobs: Any = field(default_factory=list)
    queued_notifications: List[str] = field(default_factory=list)

    boot_monotonic: float = field(default_factory=time.perf_counter)
    health_status: HealthStatus = field(default_factory=HealthStatus)

    _lock: threading.RLock = field(
        default_factory=threading.RLock,
        init=False,
        repr=False,
        compare=False,
    )

    def safe_update(self, **changes: Any) -> None:
        with self._lock:
            for key, value in changes.items():
                if not hasattr(self, key):
                    raise AttributeError(f"unknown LenaGlobalState field: {key}")
                setattr(self, key, value)

    def push_notification(self, message: str) -> None:
        with self._lock:
            self.queued_notifications.append(str(message))
            if len(self.queued_notifications) > self.MAX_NOTIFICATIONS:
                del self.queued_notifications[:-self.MAX_NOTIFICATIONS]

    def set_initialized(self, value: bool) -> None:
        with self._lock:
            self.initialized = bool(value)

    def set_boot_failure(self, reason: str) -> None:
        with self._lock:
            self.boot_failure_reason = str(reason or "")

    def set_workspace_index_status(self, value: bool) -> None:
        with self._lock:
            self.workspace_index_status = bool(value)

    def set_health(self, health: HealthStatus) -> None:
        with self._lock:
            self.health_status = health

    def register_module(self, name: str, value: object = True) -> None:
        with self._lock:
            self.loaded_modules[name] = value

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            active_jobs = (
                dict(self.active_jobs)
                if isinstance(self.active_jobs, dict)
                else list(self.active_jobs)
            )
            return {
                "initialized": self.initialized,
                "boot_failure_reason": self.boot_failure_reason,
                "permission_status": dict(self.permission_status),
                "workspace_index_status": self.workspace_index_status,
                "loaded_modules": dict(self.loaded_modules),
                "active_jobs": active_jobs,
                "queued_notifications": list(self.queued_notifications),
                "boot_monotonic": self.boot_monotonic,
                "health_status": HealthStatus(
                    cpu_percent=self.health_status.cpu_percent,
                    memory_percent=self.health_status.memory_percent,
                    process_uptime_seconds=self.health_status.process_uptime_seconds,
                ),
            }

    def render_status(self) -> str:
        snapshot = self.snapshot()
        health = snapshot["health_status"]

        loaded = ", ".join(
            f"{k}={v}" for k, v in snapshot["loaded_modules"].items()
        ) if snapshot["loaded_modules"] else "nenhum"

        perms = (
            ", ".join(f"{k}={v}" for k, v in snapshot["permission_status"].items())
            if snapshot["permission_status"] else "não verificado"
        )

        return (
            "LENA STATUS PAGE\n"
            f"initialized: {snapshot['initialized']}\n"
            f"boot_failure_reason: {snapshot['boot_failure_reason']}\n"
            f"cpu: {health.cpu_percent}%\n"
            f"memory: {health.memory_percent}%\n"
            f"uptime: {round(health.process_uptime_seconds, 2)}s\n"
            f"permissions: {perms}\n"
            f"modules: {loaded}\n"
            f"active_jobs: {len(snapshot['active_jobs'])}\n"
            f"queued_notifications: {len(snapshot['queued_notifications'])}\n"
            f"workspace indexed: {snapshot['workspace_index_status']}"
        )
