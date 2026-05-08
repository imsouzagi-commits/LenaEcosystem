from __future__ import annotations

from typing import Any

from openjarvis.lena.lena_speech_cortex import LenaSpeechCortex
from openjarvis.lena.semantic_packet import LenaSemanticPacket


class LenaResponseSynthesizer:
    _speech = LenaSpeechCortex()

    @classmethod
    def synthesize(
        cls,
        agent: Any,
        user_text: str,
        semantic_mode: str = "neutral",
        tool_payload: str = "",
        topic: str = "generic",
        mode: str = "mirror",
        stance: str = "observe",
        semantic_packet: LenaSemanticPacket | None = None,
    ) -> str:
        return cls._speech.generate(
            agent=agent,
            user_text=user_text,
            semantic_mode=semantic_mode,
            tool_payload=tool_payload,
            topic=topic,
            mode=mode,
            stance=stance,
            semantic_packet=semantic_packet,
        )
