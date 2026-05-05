from __future__ import annotations

from openjarvis.lena.action_guard import LenaActionGuard


class LenaRuntimeGuard:
    PROTECTED_APPS = LenaActionGuard.PROTECTED_APPS

    @classmethod
    def can_close(cls, app_name: str) -> bool:
        return app_name not in cls.PROTECTED_APPS
