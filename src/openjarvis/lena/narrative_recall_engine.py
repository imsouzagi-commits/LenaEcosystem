from __future__ import annotations

import random
import time


class LenaNarrativeRecallEngine:
    THREAD_TTL = 1800

    @classmethod
    def _alive(cls, memory) -> bool:
        if not memory.narrative_state.last_unresolved_ts:
            return False
        return (time.time() - memory.narrative_state.last_unresolved_ts) <= cls.THREAD_TTL

    @classmethod
    def dominant_user_thread(cls, memory) -> dict | None:
        if not cls._alive(memory):
            return None

        threads = [x for x in memory.narrative_state.unresolved_user_threads if isinstance(x, dict) and x.get("raw")]
        return threads[-1] if threads else None

    @classmethod
    def dominant_assistant_loop(cls, memory) -> dict | None:
        if not cls._alive(memory):
            return None

        loops = [x for x in memory.narrative_state.assistant_open_loops if isinstance(x, dict) and x.get("raw")]
        return loops[-1] if loops else None

    @classmethod
    def render_callback_fragment(cls, memory, topic: str) -> str | None:
        thread = cls.dominant_user_thread(memory)

        if thread:
            lowered = str(thread.get("raw", "")).lower()
            markers = set(thread.get("markers", []))

            if topic == "uncertainty" and (markers or any(x in lowered for x in ("fecha", "encaixa", "organiza", "juntar", "nebul", "confus"))):
                return random.choice([
                    "você ainda ficou preso naquela falta de encaixe.",
                    "aquilo de não conseguir organizar continua vivo.",
                    "essa sensação de pensamento sem fechamento ainda ficou aqui.",
                ])

            if topic == "fatigue" and (markers or any(x in lowered for x in ("cans", "exaust", "sem energia", "render", "força"))):
                return random.choice([
                    "aquele desgaste ainda não saiu do teu corpo.",
                    "o fio desse cansaço ainda ficou correndo.",
                    "isso ainda parece continuação daquela exaustão.",
                ])

            if topic == "distress" and (markers or any(x in lowered for x in ("pesado", "mal", "ans", "press", "sufoc"))):
                return random.choice([
                    "aquilo ainda continua te apertando por dentro.",
                    "esse peso não ficou para trás.",
                    "isso ainda parece continuação da mesma pressão.",
                ])

        loop = cls.dominant_assistant_loop(memory)
        if loop:
            return random.choice([
                "a gente ainda não encerrou o fio disso.",
                "isso ficou aberto entre uma resposta e outra.",
            ])

        return None
