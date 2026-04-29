from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(slots=True)
class SocialSignal:
    social_mode: str
    intimacy_level: float
    emotional_pressure: float
    reflection_pull: float
    user_neediness: float
    validation_need: float
    abandonment_fear: float
    existential_depth: float
    conversation_tension: float
    recommended_tone: str
    recommended_length: str
    social_directive: str


class LenaSocialEngine:
    def analyze(self, user_text: str, memory: Dict[str, Any]) -> SocialSignal:
        lowered = user_text.lower().strip()

        intimacy_level = min(
            self._safe_float(memory.get("relationship_warmth", 0.0))
            + self._safe_float(memory.get("user_attachment_score", 0.0)) * 0.8,
            1.0,
        )

        emotional_pressure = self._measure_emotional_pressure(lowered)
        reflection_pull = self._measure_reflection_pull(lowered)
        user_neediness = self._measure_neediness(lowered)
        validation_need = self._measure_validation_need(lowered)
        abandonment_fear = self._measure_abandonment_fear(lowered)
        existential_depth = self._measure_existential_depth(lowered)
        conversation_tension = self._measure_tension(lowered)

        social_mode = self._resolve_social_mode(
            emotional_pressure=emotional_pressure,
            reflection_pull=reflection_pull,
            user_neediness=user_neediness,
            validation_need=validation_need,
            abandonment_fear=abandonment_fear,
            existential_depth=existential_depth,
            intimacy_level=intimacy_level,
            conversation_tension=conversation_tension,
        )

        recommended_tone = self._resolve_tone(social_mode)
        recommended_length = self._resolve_length(social_mode)

        social_directive = self._build_directive(
            social_mode=social_mode,
            tone=recommended_tone,
            length=recommended_length,
            intimacy=intimacy_level,
            emotional_pressure=emotional_pressure,
            tension=conversation_tension,
        )

        return SocialSignal(
            social_mode=social_mode,
            intimacy_level=intimacy_level,
            emotional_pressure=emotional_pressure,
            reflection_pull=reflection_pull,
            user_neediness=user_neediness,
            validation_need=validation_need,
            abandonment_fear=abandonment_fear,
            existential_depth=existential_depth,
            conversation_tension=conversation_tension,
            recommended_tone=recommended_tone,
            recommended_length=recommended_length,
            social_directive=social_directive,
        )

    def _resolve_social_mode(
        self,
        *,
        emotional_pressure: float,
        reflection_pull: float,
        user_neediness: float,
        validation_need: float,
        abandonment_fear: float,
        existential_depth: float,
        intimacy_level: float,
        conversation_tension: float,
    ) -> str:
        if abandonment_fear >= 0.55 or validation_need >= 0.55:
            return "attachment"

        if emotional_pressure >= 0.45:
            return "emotional"

        if existential_depth >= 0.40 or reflection_pull >= 0.45:
            return "introspective"

        if user_neediness >= 0.35 and intimacy_level >= 0.25:
            return "attachment"

        if conversation_tension >= 0.40:
            return "careful"

        return "casual_light"

    def _resolve_tone(self, mode: str) -> str:
        mapping = {
            "attachment": "warm_close",
            "emotional": "soft_grounding",
            "introspective": "deep_reflective",
            "careful": "measured",
            "casual_light": "light_human",
        }
        return mapping.get(mode, "light_human")

    def _resolve_length(self, mode: str) -> str:
        mapping = {
            "attachment": "short_medium",
            "emotional": "medium",
            "introspective": "medium_long",
            "careful": "short_medium",
            "casual_light": "short",
        }
        return mapping.get(mode, "short")

    def _build_directive(
        self,
        *,
        social_mode: str,
        tone: str,
        length: str,
        intimacy: float,
        emotional_pressure: float,
        tension: float,
    ) -> str:
        return (
            f"Modo social atual: {social_mode}. "
            f"Tom recomendado: {tone}. "
            f"Tamanho ideal: {length}. "
            f"Intimidade percebida: {intimacy:.2f}. "
            f"Pressão emocional: {emotional_pressure:.2f}. "
            f"Tensão conversacional: {tension:.2f}. "
            "Responder naturalmente, sem repetir instruções, sem ecoar prompt, sem frases genéricas."
        )

    def _measure_emotional_pressure(self, text: str) -> float:
        markers = ["triste", "cansado", "mal", "ansioso", "sozinho", "vazio", "desanimado"]
        return 0.6 if any(marker in text for marker in markers) else 0.0

    def _measure_reflection_pull(self, text: str) -> float:
        markers = ["acho que", "não sei", "sei lá", "às vezes", "as vezes", "me sinto"]
        return 0.55 if any(marker in text for marker in markers) else 0.0

    def _measure_neediness(self, text: str) -> float:
        markers = ["fala comigo", "fica comigo", "quero conversar", "você tá aí", "ta ai", "ta aí"]
        return 0.5 if any(marker in text for marker in markers) else 0.0

    def _measure_validation_need(self, text: str) -> float:
        markers = ["você acha que eu", "eu sou ruim", "sou insuficiente", "sou chato"]
        return 0.6 if any(marker in text for marker in markers) else 0.0

    def _measure_abandonment_fear(self, text: str) -> float:
        markers = ["não me deixa", "fica aqui", "não some", "não vai embora"]
        return 0.65 if any(marker in text for marker in markers) else 0.0

    def _measure_existential_depth(self, text: str) -> float:
        markers = ["sentido da vida", "quem sou eu", "nada faz sentido", "existência"]
        return 0.55 if any(marker in text for marker in markers) else 0.0

    def _measure_tension(self, text: str) -> float:
        markers = ["me responde", "agora", "fala sério", "porra"]
        return 0.45 if any(marker in text for marker in markers) else 0.0

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value)
        except Exception:
            return 0.0