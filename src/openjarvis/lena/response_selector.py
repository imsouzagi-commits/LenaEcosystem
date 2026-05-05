from __future__ import annotations

from openjarvis.lena.lena_speech_cortex import LenaSpeechCortex
from openjarvis.lena.phenomenology_signal_engine import LenaPhenomenologySignalEngine

_CORTEX = LenaSpeechCortex()


class LenaResponseSelector:
    @staticmethod
    def choose(agent, user_text: str, topic: str, stage: int, mode: str, stance: str = "observe") -> str:
        packet = LenaPhenomenologySignalEngine.resolve(agent, topic)
        return _CORTEX.generate(
            agent,
            user_text,
            semantic_mode="relational",
            topic=packet["primary"],
            secondary_topic=packet["secondary"],
            latent_topic=packet["latent"],
            mode=mode,
            stance=stance,
        )

    @staticmethod
    def choose_greeting(agent, topic: str, stage: int) -> str:
        return _CORTEX.generate(agent, "", semantic_mode="greeting")
