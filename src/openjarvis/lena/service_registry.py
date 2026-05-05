from __future__ import annotations

import threading


class LenaServiceRegistry:
    def __init__(self) -> None:
        self._services: dict[str, object] = {}
        self._lock = threading.RLock()

    def register(self, name: str, service: object) -> None:
        with self._lock:
            self._services[name] = service

    def get(self, name: str) -> object | None:
        with self._lock:
            return self._services.get(name)

    def exists(self, name: str) -> bool:
        with self._lock:
            return name in self._services

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            return dict(self._services)