from __future__ import annotations

import random
import time


class LenaIntentionRecallEngine:
    TTL = 1500

    @classmethod
    def latest_open_intention(cls, memory) -> dict | None:
        intentions = list(memory.intention_state.open_intentions)
        if not intentions:
            return None

        latest = intentions[-1]
        if (time.time() - float(latest.get("ts", 0.0))) > cls.TTL:
            return None

        return latest

    @classmethod
    def render_fragment(cls, memory, topic: str) -> str | None:
        latest = cls.latest_open_intention(memory)
        if not latest:
            return None

        kind = latest.get("kind", "")

        if kind == "exploration":
            return random.choice([
                "eu ainda tô tentando localizar melhor isso contigo.",
                "eu ainda tô seguindo esse ponto que ficou aberto.",
                "a gente ainda tá no meio dessa leitura.",
            ])

        if kind == "contain":
            return random.choice([
                "eu ainda não soltei esse fio.",
                "isso ainda tá sendo segurado aqui.",
            ])

        if kind == "reflective_hold":
            return random.choice([
                "eu ainda tava acompanhando isso internamente.",
                "esse movimento ainda não tinha fechado para mim.",
            ])

        return None
