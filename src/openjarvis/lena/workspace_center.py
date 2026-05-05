from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class LenaWorkspaceCenter:
    ROOT = PROJECT_ROOT

    SNAPSHOTS = ROOT / "snapshots"
    LOGS = ROOT / "logs"
    MEMORY = ROOT / "memory"
    DELIVERY = ROOT / "delivery"
    CACHE = ROOT / "cache"
    TEMP = ROOT / "temp"
    EXPORTS = ROOT / "exports"
    REPORTS = ROOT / "reports"

    def __init__(self) -> None:
        self.root = self.ROOT
        self.snapshots = self.SNAPSHOTS
        self.logs = self.LOGS
        self.memory = self.MEMORY
        self.delivery = self.DELIVERY
        self.cache = self.CACHE
        self.temp = self.TEMP
        self.exports = self.EXPORTS
        self.reports = self.REPORTS

    def bootstrap(self) -> None:
        for path in (
            self.SNAPSHOTS,
            self.LOGS,
            self.MEMORY,
            self.DELIVERY,
            self.CACHE,
            self.TEMP,
            self.EXPORTS,
            self.REPORTS,
        ):
            path.mkdir(parents=True, exist_ok=True)

    def render_dashboard(self) -> str:
        try:
            snapshot_files = sorted(x.name for x in self.SNAPSHOTS.iterdir() if x.is_file())
        except Exception:
            snapshot_files = []

        try:
            delivery_files = sorted(x.name for x in self.DELIVERY.iterdir() if x.is_file())
        except Exception:
            delivery_files = []

        snapshot_preview = ", ".join(snapshot_files[:8]) if snapshot_files else "nenhum"
        delivery_preview = ", ".join(delivery_files[:5]) if delivery_files else "nenhum"

        return (
            "LENA WORKSPACE PAGE\n"
            f"root: {self.root}\n"
            f"snapshots: {len(snapshot_files)} [{snapshot_preview}]\n"
            f"delivery: {len(delivery_files)} [{delivery_preview}]\n"
            f"logs: {self.LOGS}\n"
            f"memory: {self.MEMORY}"
        )


__all__ = ["PROJECT_ROOT", "LenaWorkspaceCenter"]
