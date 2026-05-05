from __future__ import annotations

import uuid

from openjarvis.lena.boot_logger import LenaBootLogger
from openjarvis.lena.persistent_store import LenaPersistentStore


class LenaJobCenter:
    @classmethod
    def start(cls, kernel, action: str, payload: str) -> str:
        job_id = str(uuid.uuid4())

        if not isinstance(kernel.state.active_jobs, dict):
            kernel.state.active_jobs = {}

        kernel.state.active_jobs[job_id] = {
            "action": action,
            "payload": payload,
            "status": "running",
        }

        try:
            LenaPersistentStore.write_job(
                {
                    "job_id": job_id,
                    "action": action,
                    "payload": payload,
                    "status": "running",
                }
            )
        except Exception as exc:
            LenaBootLogger.write(f"job center start persistence failed: {exc}")

        return job_id

    @classmethod
    def finish(cls, kernel, job_id: str, status: str) -> None:
        if not isinstance(kernel.state.active_jobs, dict):
            kernel.state.active_jobs = {}

        job = kernel.state.active_jobs.get(job_id, {})

        try:
            LenaPersistentStore.write_job(
                {
                    "job_id": job_id,
                    "action": job.get("action", "unknown"),
                    "payload": job.get("payload", "unknown"),
                    "status": status,
                }
            )
        except Exception as exc:
            LenaBootLogger.write(f"job center finish persistence failed: {exc}")

        kernel.state.active_jobs.pop(job_id, None)
