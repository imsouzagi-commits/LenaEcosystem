from __future__ import annotations

from typing import Any


class LenaDiagnosticsCenter:
    @staticmethod
    def snapshot(kernel: Any) -> dict[str, Any]:
        registry = getattr(kernel, "registry", {}) or {}
        state = getattr(kernel, "state", None)

        workspace_index = registry.get("workspace_index")
        workspace_index_size = len(workspace_index) if isinstance(workspace_index, dict) else 0

        loaded_modules = getattr(state, "loaded_modules", {}) if state else {}
        permission_status = getattr(state, "permission_status", {}) if state else {}
        health = getattr(state, "health_status", None)

        return {
            "initialized": bool(getattr(state, "initialized", False)),
            "active_jobs": len(getattr(state, "active_jobs", [])),
            "loaded_modules": list(loaded_modules.keys()) if isinstance(loaded_modules, dict) else [],
            "permission_status": dict(permission_status) if isinstance(permission_status, dict) else {},
            "workspace_index_status": getattr(state, "workspace_index_status", "unknown"),
            "workspace_index_size": workspace_index_size,
            "current_expert_mode": getattr(state, "current_expert_mode", "unknown"),
            "queued_notifications": len(getattr(state, "queued_notifications", [])),
            "health_status": {
                "cpu_percent": getattr(health, "cpu_percent", 0.0),
                "memory_percent": getattr(health, "memory_percent", 0.0),
                "process_uptime_seconds": getattr(health, "process_uptime_seconds", 0.0),
            },
        }
