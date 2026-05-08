from __future__ import annotations

from openjarvis.lena.boot_logger import LenaBootLogger


class LenaSemanticTrace:

    @classmethod
    def packet(cls, packet) -> None:
        if packet is None:
            return

        if not hasattr(packet, "primary_topic"):
            return

        LenaBootLogger.write(
            (
                "[SEMANTIC] "
                f"topic={packet.primary_topic} "
                f"secondary={packet.secondary_topic} "
                f"latent={packet.latent_topic} "
                f"spread={packet.topic_spread} "
                f"pressure={packet.response_pressure} "
                f"continuity={packet.continuity_stage} "
                f"recurrence={packet.recurrence} "
                f"resonance={packet.memory_resonance}"
            )
        )
