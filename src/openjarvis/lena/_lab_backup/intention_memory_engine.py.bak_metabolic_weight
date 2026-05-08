from __future__ import annotations

import time

from openjarvis.lena.intention_state import LenaIntentionState


class LenaIntentionMemoryEngine:
    MAX_ITEMS = 8

    @staticmethod
    def restore(value) -> LenaIntentionState:
        if not isinstance(value, dict):
            return LenaIntentionState()

        state = LenaIntentionState()

        if isinstance(value.get("open_intentions"), list):
            restored = []
            for item in value["open_intentions"]:
                if isinstance(item, dict):
                    restored.append(
                        {
                            "kind": str(item.get("kind", "")),
                            "topic": str(item.get("topic", "")),
                            "prompt": str(item.get("prompt", "")),
                            "ts": float(item.get("ts", 0.0)),
                        }
                    )
            state.open_intentions = restored[-LenaIntentionMemoryEngine.MAX_ITEMS:]

        return state

    @staticmethod
    def export(state: LenaIntentionState) -> dict:
        return {
            "open_intentions": list(state.open_intentions)[-LenaIntentionMemoryEngine.MAX_ITEMS:]
        }

    @staticmethod
    def capture(memory, kind: str, topic: str, prompt: str) -> None:
        packet = {
            "kind": kind,
            "topic": topic,
            "prompt": prompt.strip(),
            "ts": time.time(),
        }

        memory.intention_state.open_intentions.append(packet)
        memory.intention_state.open_intentions = memory.intention_state.open_intentions[-LenaIntentionMemoryEngine.MAX_ITEMS:]
