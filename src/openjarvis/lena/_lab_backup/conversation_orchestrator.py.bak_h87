from __future__ import annotations

from openjarvis.lena.response_synthesizer import LenaResponseSynthesizer
from openjarvis.lena.response_selector import LenaResponseSelector
from openjarvis.lena.continuity_engine import LenaContinuityEngine
from openjarvis.lena.organic_response_composer import OrganicResponseComposer
from openjarvis.lena.unified_mental_state import LenaUnifiedMentalStateResolver


class LenaConversationOrchestrator:
    PRONOUN_AMBIGUOUS = (
        "e quem era ele?", "quem era ele?", "e quem era ela?", "quem era ela?",
        "quem é ele?", "quem é ela?", "quem e ele?", "quem e ela?",
    )

    SIMPLE_GREETINGS = {"oi", "oi lena", "olá", "ola"}

    def _tool_grounded_response(self, agent, user_text: str, tool_mode: str, tool_payload: str) -> str:
        return LenaResponseSynthesizer.synthesize(agent, user_text, tool_mode, tool_payload)

    def respond(self, agent, user_text: str, cognitive=None, tool_payload: str = "") -> str | None:
        memory = agent.memory_engine
        lowered = user_text.lower().strip()

        if lowered in self.PRONOUN_AMBIGUOUS:
            return "de quem você tá falando?"

        mental = LenaUnifiedMentalStateResolver.resolve(user_text, cognitive, memory)
        continuity = LenaContinuityEngine.resolve(memory, mental.topic)

        if tool_payload and mental.tool_mode in {"practical", "factual"}:
            return self._tool_grounded_response(agent, user_text, mental.tool_mode, tool_payload)

        if lowered in self.SIMPLE_GREETINGS:
            return LenaResponseSynthesizer.synthesize(agent, user_text, "greeting")

        if mental.memory_probe:
            return memory.answer_memory_question(lowered)

        if mental.personal_absorb:
            return LenaResponseSynthesizer.synthesize(agent, user_text, "fact_absorb")

        if mental.domain == "social":
            return LenaResponseSynthesizer.synthesize(agent, user_text, "social")

        if mental.domain == "neutral_conversational":
            return LenaResponseSynthesizer.synthesize(agent, user_text, "neutral")

        if mental.domain == "relational":
            active_topic = continuity["topic"] or mental.topic
            active_mode = mental.speech_mode
            active_stance = mental.stance_bias

            if continuity["stage"] >= 2:
                active_mode = "continuity"
            if continuity["response_pressure"] >= 4:
                active_stance = "compress"

            return LenaResponseSynthesizer.synthesize(
                agent,
                user_text,
                "relational",
                topic=active_topic,
                mode=active_mode,
                stance=active_stance,
            )

        return OrganicResponseComposer.compose_utilitarian("generic")
