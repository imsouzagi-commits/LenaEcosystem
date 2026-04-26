from __future__ import annotations

from openjarvis.intelligence.uo_action_schema import UOBatch


class UOExecutionPlan:
    def __init__(self, batch: UOBatch):
        self.batch = batch

    @property
    def commands(self):
        return self.batch.commands

    @property
    def valid(self) -> bool:
        return self.batch.valid