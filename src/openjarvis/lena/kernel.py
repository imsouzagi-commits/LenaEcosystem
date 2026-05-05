from __future__ import annotations

import threading
import time

import psutil

from openjarvis.lena.boot_logger import LenaBootLogger
from openjarvis.lena.kernel_watchdog import LenaKernelWatchdog
from openjarvis.lena.permission_center import LenaPermissionCenter
from openjarvis.lena.service_registry import LenaServiceRegistry
from openjarvis.lena.state_center import HealthStatus, LenaGlobalState
from openjarvis.lena.workspace_center import LenaWorkspaceCenter


class LenaKernel:
    _instance = None
    _instance_lock = threading.RLock()
    _booted = False

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super(LenaKernel, cls).__new__(cls)
            return cls._instance

    def __init__(self) -> None:
        with self.__class__._instance_lock:
            if LenaKernel._booted:
                return

            self.state = LenaGlobalState()
            self.registry = LenaServiceRegistry()
            self.workspace_center = LenaWorkspaceCenter()
            self.boot_completed = threading.Event()
            self.shutdown_event = threading.Event()
            self.watchdog: LenaKernelWatchdog | None = None
            LenaKernel._booted = True

            self._boot_thread = threading.Thread(
                target=self._start_async_bootstrap,
                name="lena-kernel-bootstrap",
                daemon=True,
            )
            self._boot_thread.start()

    def _boot_stage(self, name: str, fn) -> bool:
        try:
            fn()
            self.state.register_module(name, True)
            return True
        except Exception as exc:
            self.state.register_module(name, False)
            self.state.push_notification(f"{name}_bootstrap_error:{exc}")
            LenaBootLogger.write(f"{name} bootstrap fail: {exc}")
            return False

    def _start_async_bootstrap(self) -> None:
        try:
            self._boot_stage("workspace_center", self.workspace_center.bootstrap)

            def _permissions() -> None:
                permissions = LenaPermissionCenter.probe()
                self.state.safe_update(permission_status=permissions)

            self._boot_stage("permission_center", _permissions)

            def _workspace_registry() -> None:
                self.registry.register("workspace_index", {})
                self.state.set_workspace_index_status(False)

            registry_ok = self._boot_stage("workspace_indexer", _workspace_registry)

            health_ok = self._boot_stage("health_refresh", self._refresh_health)

            self.state.set_initialized(True)

            def _watchdog() -> None:
                self.watchdog = LenaKernelWatchdog(self, self.shutdown_event)
                self.watchdog.start()

            self._boot_stage("kernel_watchdog", _watchdog)

            LenaBootLogger.write(
                f"kernel bootstrap completed degraded={not all([registry_ok, health_ok])}"
            )
        except Exception as exc:
            self.state.set_boot_failure(str(exc))
            self.state.push_notification(f"kernel_bootstrap_error:{exc}")
            LenaBootLogger.write(f"kernel bootstrap fatal fail: {exc}")
        finally:
            self.boot_completed.set()

    def await_ready(self, timeout: float = 5.0) -> bool:
        completed = self.boot_completed.wait(timeout=timeout)
        if not completed:
            return False
        return bool(self.state.snapshot()["initialized"])

    def shutdown(self) -> None:
        self.shutdown_event.set()

        if self.watchdog:
            try:
                self.watchdog.stop()
            except Exception as exc:
                LenaBootLogger.write(f"kernel watchdog stop failed: {exc}")

        if self._boot_thread.is_alive():
            self._boot_thread.join(timeout=2.0)

        LenaBootLogger.write("kernel shutdown completed")

    def _refresh_health(self) -> None:
        try:
            uptime = time.perf_counter() - self.state.boot_monotonic

            self.state.set_health(
                HealthStatus(
                    cpu_percent=psutil.cpu_percent(),
                    memory_percent=psutil.virtual_memory().percent,
                    process_uptime_seconds=uptime,
                )
            )
        except Exception as exc:
            LenaBootLogger.write(f"kernel refresh health failed: {exc}")
