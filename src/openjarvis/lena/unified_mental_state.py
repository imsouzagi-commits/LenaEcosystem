from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LenaUnifiedMentalState:
    domain: str
    topic: str
    speech_mode: str
    stance_bias: str
    tool_mode: str
    explicit_question: bool
    personal_absorb: bool
    memory_probe: bool


class LenaUnifiedMentalStateResolver:
    @staticmethod
    def resolve(user_text: str, cognitive, memory) -> LenaUnifiedMentalState:
        lowered = user_text.lower().strip()
        social = memory.social_state
        if cognitive.domain in {"social", "personal"}:
            topic = "social_contact"
        elif cognitive.semantic_topic:
            topic = cognitive.semantic_topic
        elif len(lowered.split()) <= 2:
            topic = "social_contact"
        else:
            topic = memory._contextual_semantic_topic(lowered) or "generic"

        explicit_question = cognitive.is_question
        personal_absorb = cognitive.is_personal_statement
        memory_probe = cognitive.domain == "memory_probe"

        if cognitive.domain == "neutral":
            return LenaUnifiedMentalState(
                domain="neutral_conversational",
                topic="social_contact",
                speech_mode="mirror",
                stance_bias="observe",
                tool_mode="none",
                explicit_question=False,
                personal_absorb=False,
                memory_probe=False,
            )

        if cognitive.domain in {"practical", "factual"}:
            return LenaUnifiedMentalState(
                domain=cognitive.domain,
                topic=topic,
                speech_mode="grounded",
                stance_bias="observe",
                tool_mode=cognitive.domain,
                explicit_question=explicit_question,
                personal_absorb=personal_absorb,
                memory_probe=memory_probe,
            )

        if cognitive.domain == "semantic_relational":
            return LenaUnifiedMentalState(
                domain="relational",
                topic=cognitive.semantic_topic or topic,
                speech_mode="continuity" if memory._is_contextual_continuation(lowered) else "mirror",
                stance_bias="pattern_link",
                tool_mode="none",
                explicit_question=explicit_question,
                personal_absorb=False,
                memory_probe=False,
            )

        if cognitive.domain == "social":
            return LenaUnifiedMentalState(
                domain="social",
                topic=topic,
                speech_mode="engage",
                stance_bias="locate",
                tool_mode="none",
                explicit_question=explicit_question,
                personal_absorb=personal_absorb,
                memory_probe=memory_probe,
            )

        if social.unresolved_loops >= 5:
            speech_mode = "invite"
        elif social.emotional_tension >= 3:
            speech_mode = "continuity"
        elif social.reflection_depth >= 4:
            speech_mode = "contain"
        else:
            speech_mode = "mirror"

        if social.unresolved_loops >= 6:
            stance = "compress"
        elif social.reflection_depth >= 4:
            stance = "pattern_link"
        elif explicit_question:
            stance = "probe"
        else:
            stance = "observe"

        neutral_short = (
            cognitive.domain == "neutral"
            and len(lowered.split()) <= 3
            and not cognitive.semantic_topic
            and not explicit_question
        )

        return LenaUnifiedMentalState(
            domain="neutral_conversational" if neutral_short or cognitive.domain == "neutral" else "relational",
            topic=topic,
            speech_mode=speech_mode,
            stance_bias=stance,
            tool_mode="none",
            explicit_question=explicit_question,
            personal_absorb=personal_absorb,
            memory_probe=memory_probe,
        )
