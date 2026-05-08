from __future__ import annotations

from openjarvis.lena.phenomenology.cognitive_state import (
    CognitiveState,
)

from openjarvis.lena.semantic_packet import (
    LenaSemanticPacket,
)


class SemanticDriftEngine:

    @classmethod
    def apply(
        cls,
        packet: LenaSemanticPacket,
        state: CognitiveState,
    ) -> LenaSemanticPacket:

        same_topic = (
            state.active_topic ==
            packet.primary_topic
        )

        if (
            state.active_topic
            and not same_topic
            and state.semantic_inertia >= 2.4
        ):
            packet.latent_topic = (
                state.active_topic
            )

        if (
            state.continuity_residue >= 4.2
            and packet.continuity_stage < 2
        ):
            packet.continuity_stage += 1

        if (
            state.emotional_residue >= 5.0
            and packet.response_pressure < 6
        ):
            packet.response_pressure += 1

        if (
            packet.latent_topic
            and packet.mode == "mirror"
        ):
            packet.mode = "continuity"

        if (
            packet.latent_topic
            and packet.primary_topic != "neutral"
            and packet.response_pressure < 7
        ):
            packet.response_pressure += 1

        return packet
