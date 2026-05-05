from __future__ import annotations


class LenaClosureCognitionEngine:
    RESOLUTION_MARKERS = (
        "acho que sim",
        "agora fez sentido",
        "faz sentido",
        "entendi",
        "então é isso",
        "talvez seja isso",
        "melhorou",
        "clareou",
        "clareou um pouco",
        "acho que consegui ver",
        "acho que enxerguei",
        "sim, isso",
        "é isso",
        "ok entendi",
    )

    SOFT_RELIEF_MARKERS = (
        "um pouco melhor",
        "menos pesado",
        "mais claro",
        "deu uma aliviada",
        "acho que sim",
        "talvez",
    )

    
    @classmethod
    def ingest(cls, memory, user_text: str) -> None:
        lowered = user_text.lower().strip()
        social = memory.social_state

        if any(x in lowered for x in cls.RESOLUTION_MARKERS):
            social.unresolved_loops = max(0, social.unresolved_loops - 3)
            social.emotional_tension = max(0, social.emotional_tension - 2)
            social.presence_momentum = max(0, social.presence_momentum - 2)
            social.current_conversation_arc = "resolving"
            memory.narrative_state.assistant_open_loops = memory.narrative_state.assistant_open_loops[-1:]
            memory.intention_state.open_intentions = memory.intention_state.open_intentions[-1:]
            return

        if any(x in lowered for x in cls.SOFT_RELIEF_MARKERS):
            social.unresolved_loops = max(0, social.unresolved_loops - 1)
            social.emotional_tension = max(0, social.emotional_tension - 1)
            social.presence_momentum = max(0, social.presence_momentum - 1)
            social.current_conversation_arc = "softening"
