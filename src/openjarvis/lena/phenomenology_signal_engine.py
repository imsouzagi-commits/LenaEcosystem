from __future__ import annotations


class LenaPhenomenologySignalEngine:
    @staticmethod
    def _fallback(topic: str | None) -> dict:
        topic = topic or "uncertainty"
        return {
            "primary": topic,
            "secondary": topic,
            "latent": topic,
        }

    @staticmethod
    def resolve(memory, current_topic: str | None) -> dict:
        if not current_topic:
            return LenaPhenomenologySignalEngine._fallback("uncertainty")

        primary = current_topic
        secondary = current_topic
        latent = current_topic

        suspended = list(memory.narrative_state.suspended_topics)[-3:]
        recurrent = sorted(memory.topic_counters.items(), key=lambda x: x[1], reverse=True)

        if suspended:
            for tp in reversed(suspended):
                if tp != primary:
                    latent = tp
                    break

        if recurrent:
            for tp, _ in recurrent:
                if tp != primary:
                    secondary = tp
                    break

        unresolved = list(memory.narrative_state.unresolved_user_threads)[-2:]
        joined = " ".join(x.get("raw", "").lower() for x in unresolved)

        if any(x in joined for x in ("encaixa", "juntar", "desencontro")):
            secondary = "disconnection"

        if any(x in joined for x in ("fecha", "concluir", "organiza", "entender")):
            secondary = "clarity_seek"

        if any(x in joined for x in ("continua", "mesmo", "parado", "não sai")):
            latent = "stagnation"

        return {
            "primary": primary,
            "secondary": secondary,
            "latent": latent,
        }
