from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MemoryState:
    user_name: Optional[str] = None
    user_mood: Optional[str] = None
    user_role: Optional[str] = None

    user_preferences: List[str] = field(default_factory=list)
    active_projects: List[str] = field(default_factory=list)
    conversation_facts: List[str] = field(default_factory=list)
    emotional_history: List[str] = field(default_factory=list)

    style_preferences: List[str] = field(default_factory=list)
    psychological_traits: List[str] = field(default_factory=list)
    relational_needs: List[str] = field(default_factory=list)
    interaction_patterns: List[str] = field(default_factory=list)

    conversation_mode: str = "neutral"
    relationship_warmth: float = 0.35

    last_topics: List[str] = field(default_factory=list)
    last_emotional_statement: Optional[str] = None

    user_attachment_score: float = 0.0
    user_openness_score: float = 0.0
    user_curiosity_score: float = 0.0
    user_reflection_score: float = 0.0
    user_control_score: float = 0.0


class MemoryManager:
    def __init__(self) -> None:
        self.state = MemoryState()

    def get_state(self) -> MemoryState:
        return self.state

    def absorb(self, text: str) -> None:
        cleaned = self._clean_text(text)
        lowered = cleaned.lower()

        if not cleaned:
            return

        self._soft_decay_scores()
        self._remember_recent_topic(cleaned)

        self._extract_identity(cleaned)
        self._extract_emotion(cleaned, lowered)
        self._extract_style_preferences(lowered)
        self._extract_relational_signals(lowered)
        self._extract_curiosity_signals(lowered)
        self._extract_reflection_signals(lowered)
        self._extract_control_signals(lowered)

        self._synthesize_psychological_traits()
        self._update_conversation_mode()
        self._compress_memory_noise()

    def _clean_text(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def _soft_decay_scores(self) -> None:
        self.state.user_attachment_score = max(0.0, self.state.user_attachment_score - 0.003)
        self.state.user_openness_score = max(0.0, self.state.user_openness_score - 0.002)
        self.state.user_curiosity_score = max(0.0, self.state.user_curiosity_score - 0.001)
        self.state.user_reflection_score = max(0.0, self.state.user_reflection_score - 0.001)
        self.state.user_control_score = max(0.0, self.state.user_control_score - 0.001)

    def _remember_recent_topic(self, text: str) -> None:
        self.state.last_topics.append(text)
        self.state.last_topics = self.state.last_topics[-30:]

    def _extract_identity(self, cleaned: str) -> None:
        name_match = re.search(r"meu nome é\s+([a-zA-ZÀ-ÿ]+)", cleaned, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).strip().title()
            self.state.user_name = name
            self._push_fact(name)

        role_match = re.search(r"\b(sou|eu sou|trabalho com)\s+(.+)", cleaned, re.IGNORECASE)
        if role_match:
            role = role_match.group(2).strip().rstrip(".")
            if 2 < len(role) < 60:
                self.state.user_role = role
                self._push_fact(role)

    def _extract_emotion(self, cleaned: str, lowered: str) -> None:
        moods = {
            "desanimado": ["desanimado", "sem vontade", "cansado", "pra baixo", "triste"],
            "ansioso": ["ansioso", "nervoso", "preocupado"],
            "feliz": ["feliz", "animado", "empolgado"],
            "confuso": ["confuso", "perdido", "sem saber"],
        }

        for mood, signals in moods.items():
            if any(signal in lowered for signal in signals):
                self.state.user_mood = mood
                self.state.last_emotional_statement = cleaned

                if not self.state.emotional_history or self.state.emotional_history[-1] != mood:
                    self.state.emotional_history.append(mood)

                self.state.emotional_history = self.state.emotional_history[-20:]
                self.state.user_openness_score = min(1.0, self.state.user_openness_score + 0.08)
                self._push_fact(mood)
                break

    def _extract_style_preferences(self, lowered: str) -> None:
        preferences = {
            "fala de forma mais natural": "prefere naturalidade",
            "você parece muito formal": "rejeita formalismo",
            "fala comigo como se fosse minha amiga": "busca intimidade conversacional",
            "me responde sinceramente": "valoriza sinceridade",
            "fala normal": "prefere naturalidade",
            "sem formalidade": "prefere naturalidade",
        }

        for trigger, pref in preferences.items():
            if trigger in lowered:
                self._push_unique(self.state.style_preferences, pref)
                self.state.user_control_score = min(1.0, self.state.user_control_score + 0.05)

    def _extract_relational_signals(self, lowered: str) -> None:
        relational_triggers = [
            "vamos conversar",
            "fala comigo",
            "às vezes parece que eu tô falando com alguém de verdade",
            "isso é estranho",
            "você tá conseguindo me entender",
            "me responde sinceramente",
            "quero conversar",
            "conversa comigo",
        ]

        if any(trigger in lowered for trigger in relational_triggers):
            self.state.user_attachment_score = min(1.0, self.state.user_attachment_score + 0.06)
            self.state.relationship_warmth = min(1.0, self.state.relationship_warmth + 0.05)
            self._push_unique(self.state.relational_needs, "procura conexão conversacional real")

    def _extract_curiosity_signals(self, lowered: str) -> None:
        curiosity_words = [
            "me explica",
            "qual a diferença",
            "quem criou",
            "o que é",
            "pesquisa no google",
            "crie uma estratégia",
            "como funciona",
            "me ensina",
        ]

        if any(word in lowered for word in curiosity_words):
            self.state.user_curiosity_score = min(1.0, self.state.user_curiosity_score + 0.05)

    def _extract_reflection_signals(self, lowered: str) -> None:
        reflection_words = [
            "o que você acha",
            "como você me percebe",
            "o que você já percebeu",
            "quem eu sou",
            "resumo completo",
            "isso te assusta",
            "se você fosse humana",
            "você tá conseguindo me entender",
            "faz um resumo",
        ]

        if any(word in lowered for word in reflection_words):
            self.state.user_reflection_score = min(1.0, self.state.user_reflection_score + 0.07)

    def _extract_control_signals(self, lowered: str) -> None:
        control_words = [
            "fala de forma",
            "fala comigo",
            "guarda isso",
            "me descreve",
            "vamos mudar de assunto",
            "me responde",
            "quero que você",
        ]

        if any(word in lowered for word in control_words):
            self.state.user_control_score = min(1.0, self.state.user_control_score + 0.05)

    def _synthesize_psychological_traits(self) -> None:
        self.state.psychological_traits.clear()
        self.state.interaction_patterns.clear()

        if self.state.user_control_score > 0.08:
            self._push_unique(self.state.psychological_traits, "diretivo")
            self._push_unique(self.state.interaction_patterns, "costuma calibrar a interação")

        if self.state.user_reflection_score > 0.10:
            self._push_unique(self.state.psychological_traits, "introspectivo")
            self._push_unique(self.state.interaction_patterns, "busca leituras profundas")

        if self.state.user_attachment_score > 0.18:
            self._push_unique(self.state.psychological_traits, "relacional")
            self._push_unique(self.state.interaction_patterns, "testa conexão emocional")

        if self.state.user_curiosity_score > 0.10:
            self._push_unique(self.state.psychological_traits, "curioso")
            self._push_unique(self.state.interaction_patterns, "alterna conversa com exploração intelectual")

        if self.state.user_openness_score > 0.12:
            self._push_unique(self.state.psychological_traits, "emocionalmente aberto")
            self._push_unique(self.state.interaction_patterns, "verbaliza estados internos")

        if self.state.relationship_warmth > 0.70:
            self._push_unique(self.state.psychological_traits, "engajado afetivamente")

    def _update_conversation_mode(self) -> None:
        if self.state.user_mood:
            self.state.conversation_mode = "emotional"
        elif self.state.user_reflection_score > 0.12:
            self.state.conversation_mode = "reflective"
        elif self.state.user_curiosity_score > self.state.user_attachment_score:
            self.state.conversation_mode = "intellectual"
        elif self.state.user_attachment_score > 0.14:
            self.state.conversation_mode = "relational"
        else:
            self.state.conversation_mode = "casual"

    def _compress_memory_noise(self) -> None:
        self.state.conversation_facts = self.state.conversation_facts[-12:]
        self.state.style_preferences = self.state.style_preferences[-8:]
        self.state.relational_needs = self.state.relational_needs[-6:]

    def _push_fact(self, value: str) -> None:
        self._push_unique(self.state.conversation_facts, value)

    @staticmethod
    def _push_unique(target: List[str], value: str) -> None:
        if value not in target:
            target.append(value)


memory = MemoryManager()