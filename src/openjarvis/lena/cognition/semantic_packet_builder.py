from __future__ import annotations

from openjarvis.lena.semantic_packet import LenaSemanticPacket
from openjarvis.lena.cognition.response_pressure_engine import (
    LenaResponsePressureEngine,
)
from openjarvis.lena.cognition.continuity_engine import (
    LenaContinuityEngine,
)


class LenaSemanticPacketBuilder:

    @classmethod
    def enrich(
        cls,
        packet: LenaSemanticPacket,
        memory,
        user_text: str,
    ) -> LenaSemanticPacket:

        lowered = user_text.lower()

        question_pressure = lowered.endswith("?")

        open_loops = len(
            getattr(memory.narrative_state, "unresolved_user_threads", [])
        )

        continuity = LenaContinuityEngine.stage(
            recurrence=packet.recurrence,
            open_loops=open_loops,
            continuity_flag=packet.continuation_flag,
        )

        packet.continuity_stage = continuity

        packet.response_pressure = LenaResponsePressureEngine.compute(
            semantic_spread=packet.topic_spread,
            continuity_stage=continuity,
            recurrence=packet.recurrence,
            memory_resonance=packet.memory_resonance,
            question_pressure=question_pressure,
            open_loops=open_loops,
        )

        return packet
