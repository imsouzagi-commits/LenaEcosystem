from __future__ import annotations

from typing import Any, Dict


class LenaSocialDynamics:
    def update_after_turn(
        self,
        memory: Dict[str, Any],
        user_text: str,
        assistant_text: str,
    ) -> Dict[str, Any]:
        updated = dict(memory)

        warmth = self._safe_float(updated.get("relationship_warmth", 0.0))
        attachment = self._safe_float(updated.get("user_attachment_score", 0.0))
        openness = self._safe_float(updated.get("user_openness_score", 0.0))
        reflection = self._safe_float(updated.get("user_reflection_score", 0.0))
        curiosity = self._safe_float(updated.get("user_curiosity_score", 0.0))
        control = self._safe_float(updated.get("user_control_score", 0.0))

        emotional_pressure = self._safe_float(updated.get("emotional_pressure", 0.0))
        conversation_tension = self._safe_float(updated.get("conversation_tension", 0.0))
        validation_need = self._safe_float(updated.get("validation_need", 0.0))
        abandonment_fear = self._safe_float(updated.get("abandonment_fear", 0.0))
        existential_depth = self._safe_float(updated.get("existential_depth", 0.0))
        urgency_score = self._safe_float(updated.get("urgency_score", 0.0))
        frustration_probability = self._safe_float(updated.get("frustration_probability", 0.0))

        lowered = user_text.lower().strip()

        if len(user_text) > 35:
            openness += 0.015

        if any(
            marker in lowered
            for marker in [
                "acho que",
                "sei lá",
                "não sei",
                "às vezes",
                "as vezes",
                "me sinto",
                "me sentindo",
                "pensando muito",
                "confuso",
                "estranho",
            ]
        ):
            reflection += 0.020
            openness += 0.012

        if any(
            marker in lowered
            for marker in [
                "to cansado",
                "tô cansado",
                "to cansada",
                "tô cansada",
                "to triste",
                "tô triste",
                "desanimado",
                "desanimada",
                "to mal",
                "tô mal",
                "sem vontade",
            ]
        ):
            emotional_pressure += 0.030
            reflection += 0.015

        if any(
            marker in lowered
            for marker in [
                "fala comigo",
                "vamos conversar",
                "quero conversar",
                "você tá aí",
                "ta ai",
                "ta aí",
                "fica comigo",
                "não some",
                "continua aqui",
            ]
        ):
            attachment += 0.025
            warmth += 0.020
            abandonment_fear += 0.020

        if any(
            marker in lowered
            for marker in [
                "me responde sinceramente",
                "o que você acha de mim",
                "você tá conseguindo me entender",
                "isso é estranho",
                "sou estranho",
                "me diz a verdade",
            ]
        ):
            validation_need += 0.030
            conversation_tension += 0.020

        if any(
            marker in lowered
            for marker in [
                "vida",
                "sentido",
                "sozinho",
                "existência",
                "real",
                "de verdade",
                "vazio",
            ]
        ):
            existential_depth += 0.030
            reflection += 0.010

        if "?" in user_text:
            curiosity += 0.010

        if any(
            marker in lowered
            for marker in [
                "faz",
                "me responde",
                "me diz",
                "quero que",
                "agora",
                "rápido",
                "anda",
            ]
        ):
            control += 0.010
            urgency_score += 0.015

        if any(
            marker in lowered
            for marker in [
                "não entendeu",
                "não foi isso",
                "errado",
                "você não está entendendo",
                "você tá formal",
                "mais natural",
            ]
        ):
            frustration_probability += 0.025
            conversation_tension += 0.015

        if len(assistant_text) < 120:
            warmth += 0.008

        updated["relationship_warmth"] = min(warmth, 1.0)
        updated["user_attachment_score"] = min(attachment, 1.0)
        updated["user_openness_score"] = min(openness, 1.0)
        updated["user_reflection_score"] = min(reflection, 1.0)
        updated["user_curiosity_score"] = min(curiosity, 1.0)
        updated["user_control_score"] = min(control, 1.0)

        updated["emotional_pressure"] = min(emotional_pressure, 1.0)
        updated["conversation_tension"] = min(conversation_tension, 1.0)
        updated["validation_need"] = min(validation_need, 1.0)
        updated["abandonment_fear"] = min(abandonment_fear, 1.0)
        updated["existential_depth"] = min(existential_depth, 1.0)
        updated["urgency_score"] = min(urgency_score, 1.0)
        updated["frustration_probability"] = min(frustration_probability, 1.0)

        return updated

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value)
        except Exception:
            return 0.0