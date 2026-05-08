from __future__ import annotations

from typing import Any

from openjarvis.lena.lena_speech_cortex import LenaSpeechCortex

_CORTEX = LenaSpeechCortex()


class LenaResponseSynthesizer:
    @staticmethod
    def synthesize(
        agent: Any,
        user_text: str,
        semantic_mode: str = "neutral",
        tool_payload: str = "",
        topic: str = "generic",
        mode: str = "mirror",
        stance: str = "observe",
    ) -> str:
        return _CORTEX.generate(
            agent,
            user_text,
            semantic_mode=semantic_mode,
            tool_payload=tool_payload,
            topic=topic,
            mode=mode,
            stance=stance,
        )
