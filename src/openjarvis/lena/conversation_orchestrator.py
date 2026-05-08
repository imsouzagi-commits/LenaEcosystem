from __future__ import annotations

from openjarvis.lena.response_synthesizer import LenaResponseSynthesizer
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

    def respond(self, agent, user_text: str, cognitive=None, tool_payload: str = "", semantic_packet=None) -> str | None:
        memory = agent.memory_engine
        lowered = user_text.lower().strip()

        if lowered in self.PRONOUN_AMBIGUOUS:
            return "de quem você tá falando?"

        mental = LenaUnifiedMentalStateResolver.resolve(user_text, cognitive, memory)

        if tool_payload and mental.tool_mode in {"practical", "factual"}:
            return self._tool_grounded_response(agent, user_text, mental.tool_mode, tool_payload)

        if lowered in self.SIMPLE_GREETINGS:
            return LenaResponseSynthesizer.synthesize(agent, user_text, "greeting")

        if mental.memory_probe:
            return memory.answer_memory_question(lowered)

        if mental.personal_absorb:
            return LenaResponseSynthesizer.synthesize(agent, user_text, "fact_absorb")

        if mental.domain in {"social", "neutral_conversational", "relational"}:
            packet = semantic_packet
            return LenaResponseSynthesizer.synthesize(
                agent,
                user_text,
                "relational",
                semantic_packet=packet,
            )

        return LenaResponseSynthesizer.synthesize(agent, user_text, "relational", semantic_packet=semantic_packet)
