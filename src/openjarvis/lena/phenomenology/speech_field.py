from __future__ import annotations

from dataclasses import dataclass

from openjarvis.lena.semantic_packet import LenaSemanticPacket


@dataclass(slots=True)
class SpeechFieldState:

    temporal_gravity: float
    semantic_density: float
    cognitive_tension: float
    subjective_depth: float
    inferential_velocity: float
    emotional_viscosity: float
    continuity_mass: float
    silence_pressure: float


class SpeechFieldResolver:

    @classmethod
    def resolve(
        cls,
        packet: LenaSemanticPacket,
    ) -> SpeechFieldState:

        temporal_gravity = cls._temporal_gravity(packet)

        semantic_density = cls._semantic_density(packet)

        cognitive_tension = cls._cognitive_tension(packet)

        subjective_depth = cls._subjective_depth(packet)

        inferential_velocity = cls._inferential_velocity(packet)

        emotional_viscosity = cls._emotional_viscosity(packet)

        continuity_mass = cls._continuity_mass(packet)

        silence_pressure = cls._silence_pressure(packet)

        return SpeechFieldState(
            temporal_gravity=temporal_gravity,
            semantic_density=semantic_density,
            cognitive_tension=cognitive_tension,
            subjective_depth=subjective_depth,
            inferential_velocity=inferential_velocity,
            emotional_viscosity=emotional_viscosity,
            continuity_mass=continuity_mass,
            silence_pressure=silence_pressure,
        )

    @staticmethod
    def _temporal_gravity(
        packet: LenaSemanticPacket,
    ) -> float:

        base = (
            (packet.continuity_stage * 1.15) +
            (packet.session_hits * 0.22)
        )

        if packet.primary_topic in {
            "stagnation",
            "fatigue",
        }:
            base += 1.4

        return round(min(10.0, base), 2)

    @staticmethod
    def _semantic_density(
        packet: LenaSemanticPacket,
    ) -> float:

        base = (
            packet.memory_resonance * 0.72
        )

        if packet.secondary_topic:
            base += 0.9

        if packet.latent_topic:
            base += 0.7

        return round(min(10.0, base), 2)

    @staticmethod
    def _cognitive_tension(
        packet: LenaSemanticPacket,
    ) -> float:

        base = (
            packet.response_pressure * 0.82
        )

        if packet.mode == "contain":
            base += 1.2

        return round(min(10.0, base), 2)

    @staticmethod
    def _subjective_depth(
        packet: LenaSemanticPacket,
    ) -> float:

        base = (
            packet.memory_resonance * 0.44
        ) + (
            packet.continuity_stage * 0.82
        )

        return round(min(10.0, base), 2)

    @staticmethod
    def _inferential_velocity(
        packet: LenaSemanticPacket,
    ) -> float:

        velocity = 5.0

        if packet.primary_topic == "mental_noise":
            velocity += 2.2

        elif packet.primary_topic == "stagnation":
            velocity -= 2.4

        elif packet.primary_topic == "fatigue":
            velocity -= 1.8

        elif packet.primary_topic == "uncertainty":
            velocity += 0.9

        return round(
            max(0.5, min(10.0, velocity)),
            2,
        )

    @staticmethod
    def _emotional_viscosity(
        packet: LenaSemanticPacket,
    ) -> float:

        viscosity = (
            packet.memory_resonance * 0.63
        )

        if packet.primary_shade:
            viscosity += 1.0

        return round(min(10.0, viscosity), 2)

    @staticmethod
    def _continuity_mass(
        packet: LenaSemanticPacket,
    ) -> float:

        mass = (
            packet.continuity_stage * 1.7
        )

        if packet.session_hits >= 4:
            mass += 1.2

        return round(min(10.0, mass), 2)

    @staticmethod
    def _silence_pressure(
        packet: LenaSemanticPacket,
    ) -> float:

        pressure = 0.0

        if packet.primary_topic in {
            "fatigue",
            "stagnation",
        }:
            pressure += 2.4

        if packet.mode == "contain":
            pressure += 1.2

        return round(min(10.0, pressure), 2)
