from __future__ import annotations


class LenaRelationalImpression:
    @staticmethod
    def infer(memory) -> str | None:
        fatigue = int(memory.topic_counters.get("fatigue", 0))
        uncertainty = int(memory.topic_counters.get("uncertainty", 0))
        distress = int(memory.topic_counters.get("distress", 0))
        familiarity = int(memory.social_state.familiarity)

        if familiarity < 3:
            return None

        if fatigue >= 4:
            return "você anda se empurrando além da energia."

        if uncertainty >= 4:
            return "você anda tentando manter o dia com a mente tropeçando."

        if distress >= 4:
            return "você anda absorvendo mais peso do que mostra."

        if fatigue >= 2 and uncertainty >= 2:
            return "você continua funcionando mesmo meio saturado."

        return None
