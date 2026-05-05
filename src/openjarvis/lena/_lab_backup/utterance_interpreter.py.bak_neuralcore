from __future__ import annotations


class LenaUtteranceInterpreter:
    @staticmethod
    def detect(user_text: str, domain: str) -> str:
        lowered = user_text.lower().strip()

        if domain in ("narrative", "emotional"):
            if any(x in lowered for x in ("ainda", "continua", "continua igual", "mesmo lugar", "aqui dentro")):
                return "continuation"

            if any(x in lowered for x in ("passou rápido", "passou voando", "o dia voou", "a tarde passou")):
                return "temporal_observation"

            if any(x in lowered for x in ("nada encaixa", "ruído mental", "mente confusa", "minha cabeça")):
                return "cognitive_disorder"

            if any(x in lowered for x in ("saturado", "cansado", "exausto", "sem render")):
                return "fatigue_signal"

            return "generic_personal"

        if domain == "practical":
            if any(x in lowered for x in ("compensa", "vale a pena", "faz sentido")):
                return "cost_benefit"
            return "practical_generic"

        if domain == "inquisitive":
            if "melhor que" in lowered or "diferença" in lowered or "diferença entre" in lowered:
                return "comparative_question"
            return "generic_question"

        return "generic"
