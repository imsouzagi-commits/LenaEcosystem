from __future__ import annotations

from openjarvis.lena.persistent_store import LenaPersistentStore


class LenaAuditLogCenter:
    @staticmethod
    def write(action_name: str, payload: str, status: str) -> None:
        LenaPersistentStore.write_audit(
            {
                "action": action_name,
                "payload": payload,
                "status": status,
            }
        )
