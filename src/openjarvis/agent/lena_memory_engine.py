from __future__ import annotations

from typing import Any, Dict, List

from openjarvis.core.types import Message
from openjarvis.memory.manager import MemoryManager


class LenaMemoryEngine:
    def __init__(self) -> None:
        self.manager = MemoryManager()

    def absorb(self, messages: List[Message]) -> None:
        for msg in messages:
            if str(msg.role).lower().endswith("user"):
                self.manager.absorb(msg.content)

    def answer_from_memory(self, text: str) -> str | None:
        lowered = text.lower().strip()
        state = self.manager.get_state()

        if "qual meu nome" in lowered and state.user_name:
            return f"Seu nome é {state.user_name}."

        if "o que eu faço" in lowered and state.user_role:
            return f"Você é {state.user_role}."

        if "me lembra como eu estou me sentindo" in lowered and state.user_mood:
            return f"Você me disse que tá {state.user_mood}."

        if "qual foi a última coisa emocional" in lowered and state.last_emotional_statement:
            return f"A última coisa emocional que você me falou foi: {state.last_emotional_statement}."

        if "o que você acha de mim" in lowered:
            return self._build_self_perception()

        if "me descreve em duas palavras" in lowered:
            return self._build_two_word_perception()

        if "faz um resumo de tudo que você sabe de mim" in lowered:
            return self._build_short_summary()

        if "faz um resumo completo da nossa conversa inteira" in lowered:
            return self._build_long_summary()

        if "quem eu sou" in lowered:
            return self._build_identity_summary()

        if "como eu estou" in lowered:
            return self._build_emotional_summary()

        if "como você me percebe" in lowered or "o que você já percebeu" in lowered:
            return self._build_deep_perception()

        return None

    def _build_self_perception(self) -> str:
        state = self.manager.get_state()

        if state.psychological_traits:
            readable = ", ".join(state.psychological_traits[:-1])

            if len(state.psychological_traits) > 1:
                readable += f" e {state.psychological_traits[-1]}"
            else:
                readable = state.psychological_traits[0]

            return (
                "Você me passa a sensação de alguém "
                f"{readable}, que não curte conversa superficial."
            )

        return "Você parece observador."

    def _build_two_word_perception(self) -> str:
        state = self.manager.get_state()

        if "diretivo" in state.psychological_traits and "curioso" in state.psychological_traits:
            return "Direto. Curioso."

        if "introspectivo" in state.psychological_traits:
            return "Analítico. Profundo."

        if "relacional" in state.psychological_traits:
            return "Próximo. Observador."

        return "Observador. Objetivo."

    def _build_short_summary(self) -> str:
        state = self.manager.get_state()
        parts: List[str] = []

        if state.user_name:
            parts.append(f"Seu nome é {state.user_name}.")
        if state.user_role:
            parts.append(f"Você é {state.user_role}.")
        if state.user_mood:
            parts.append(f"Hoje você tá {state.user_mood}.")

        if state.style_preferences:
            parts.append(
                f"Você prefere uma conversa {', '.join(state.style_preferences[:2])}."
            )

        return " ".join(parts) if parts else "Ainda sei pouca coisa sobre você."

    def _build_long_summary(self) -> str:
        state = self.manager.get_state()
        blocks: List[str] = []

        identity = self._build_identity_summary()
        emotional = self._build_emotional_summary()
        perception = self._build_deep_perception()

        if identity:
            blocks.append(identity)

        if emotional:
            blocks.append(emotional)

        if perception:
            blocks.append(perception)

        if state.last_topics:
            recent = ", ".join(state.last_topics[-6:])
            blocks.append(f"Nossa conversa passou por {recent}.")

        return " ".join(blocks)

    def _build_identity_summary(self) -> str:
        state = self.manager.get_state()
        pieces: List[str] = []

        if state.user_name:
            pieces.append(f"Seu nome é {state.user_name}")

        if state.user_role:
            pieces.append(f"você é {state.user_role}")

        if pieces:
            return ". ".join(pieces) + "."

        return ""

    def _build_emotional_summary(self) -> str:
        state = self.manager.get_state()

        if state.user_mood:
            if state.last_emotional_statement:
                return (
                    f"Emocionalmente você demonstrou estar {state.user_mood}, "
                    f"principalmente quando disse '{state.last_emotional_statement}'."
                )
            return f"Emocionalmente você demonstrou estar {state.user_mood}."

        return ""

    def _build_deep_perception(self) -> str:
        state = self.manager.get_state()
        traits = state.psychological_traits
        patterns = state.interaction_patterns

        if not traits:
            return "Ainda estou te lendo."

        trait_text = ", ".join(traits[:-1])
        if len(traits) > 1:
            trait_text += f" e {traits[-1]}"
        else:
            trait_text = traits[0]

        pattern_text = ", ".join(patterns[:2]) if patterns else ""

        response = f"Eu te percebo como alguém {trait_text}."

        if pattern_text:
            response += f" Você costuma {pattern_text}."

        if state.relational_needs:
            response += " Também dá pra sentir que você procura uma conversa que pareça real."

        return response

    def snapshot(self) -> Dict[str, Any]:
        state = self.manager.get_state()

        return {
            "user_name": state.user_name,
            "user_mood": state.user_mood,
            "user_role": state.user_role,
            "user_preferences": list(state.user_preferences),
            "active_projects": list(state.active_projects),
            "conversation_facts": list(state.conversation_facts),
            "emotional_history": list(state.emotional_history),
            "style_preferences": list(state.style_preferences),
            "psychological_traits": list(state.psychological_traits),
            "relational_needs": list(state.relational_needs),
            "interaction_patterns": list(state.interaction_patterns),
            "conversation_mode": state.conversation_mode,
            "relationship_warmth": state.relationship_warmth,
            "last_topics": list(state.last_topics),
            "last_emotional_statement": state.last_emotional_statement,
            "user_attachment_score": state.user_attachment_score,
            "user_openness_score": state.user_openness_score,
            "user_curiosity_score": state.user_curiosity_score,
            "user_reflection_score": state.user_reflection_score,
            "user_control_score": state.user_control_score,
        }
    
    def apply_social_updates(self, updates: Dict[str, Any]) -> None:
        state = self.manager.state

        state.relationship_warmth = float(updates.get("relationship_warmth", state.relationship_warmth))
        state.user_attachment_score = float(updates.get("user_attachment_score", state.user_attachment_score))
        state.user_openness_score = float(updates.get("user_openness_score", state.user_openness_score))
        state.user_reflection_score = float(updates.get("user_reflection_score", state.user_reflection_score))
        state.user_curiosity_score = float(updates.get("user_curiosity_score", state.user_curiosity_score))
        state.user_control_score = float(updates.get("user_control_score", state.user_control_score)) 