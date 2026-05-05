from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CognitiveDecision:
    domain: str
    capability: str = "none"
    query: str = ""
    semantic_topic: str = ""
    requires_conversation: bool = True
    is_question: bool = False
    is_personal_statement: bool = False
    has_external_knowledge: bool = False


class LenaCognitiveOrchestrator:
    ACTION_DESKTOP = ("abre ", "abrir ", "fecha ", "fechar ", "encerra ")
    ACTION_FILE = (
        "cria arquivo", "criar arquivo", "move arquivo", "mover arquivo",
        "deleta arquivo", "deletar arquivo", "apaga arquivo", "lista arquivos",
        "ler arquivo", "lê arquivo",
    )

    FACTUAL_WEB = (
        "pesquisa no google", "pesquise", "procura na internet", "busca na internet",
        "quem criou", "quem fundou", "quem inventou", "o que é", "o que foi",
        "quando surgiu", "quando começou", "onde fica", "quantos",
        "qual a capital", "qual é a capital", "quem é", "quem foi",
    )

    LOCAL_CODE_SEARCH = (
        "nesse código", "nesse codigo", "neste código", "neste codigo",
        "no projeto", "na pasta", "nesse arquivo", "neste arquivo",
        "procura no projeto", "busca no projeto", "analisa esse código",
        "analisa esse codigo", "acha no projeto",
    )

    PRACTICAL_MARKERS = (
        "compensa", "vale a pena", "é melhor", "e melhor", "qual melhor",
        "qual é melhor", "devo usar", "faz sentido usar", "será que uso",
        "sera que uso", "o que você recomenda", "o que voce recomenda",
        "vantagem de", "diferença entre", "diferenca entre",
    )

    TECH_OBJECTS = (
        "docker", "postgres", "mysql", "sqlite", "fastapi", "python",
        "redis", "mongodb", "api", "backend", "frontend", "websocket",
        "microserviço", "microsservico", "celery", "nginx",
    )

    MEMORY_MARKERS = (
        "qual meu nome", "qual meu nome mesmo", "você lembra meu nome", "voce lembra meu nome",
        "você lembra onde eu moro", "voce lembra onde eu moro", "eu moro onde",
        "o que eu falei que estou construindo", "qual é meu projeto", "qual e meu projeto",
    )

    PERSONAL_FACT_PREFIXES = ("meu nome é ", "eu moro em ", "curso ", "estou construindo ")


    SEMANTIC_RELATIONAL_MAP = {
        "fatigue": (
            "estou cansado", "to cansado", "tô cansado", "exausto", "sem energia",
            "muito cansado", "cansado faz dias", "energia curta",
        ),
        "disconnection": (
            "não encaixa", "nao encaixa", "sem encaixe", "desconexo",
            "partes soltas", "não conecta", "nao conecta", "sem conexão",
        ),
        "uncertainty": (
            "nebuloso", "turvo", "confuso", "não firma", "nao firma",
            "embaralhado", "não fecha", "nao fecha",
        ),
        "stagnation": (
            "nada sai do lugar", "não sai do lugar", "nao sai do lugar",
            "travado", "parado", "não anda", "nao anda", "mesmo lugar",
        ),
        "clarity_seek": (
            "organizar minha cabeça", "organizar minha cabeca", "preciso entender",
            "preciso organizar", "achar uma linha", "quero clareza",
        ),
    }

    NEUTRAL_SHORTS = {
        "oi", "ola", "olá", "ok", "certo", "hm", "hmm", "sim", "nao", "não",
        "entendi", "ta", "tá", "beleza", "blz"
    }


    


    def _starts(self, lowered: str, family: tuple[str, ...]) -> bool:
        return lowered.startswith(family)

    def _contains(self, lowered: str, family: tuple[str, ...]) -> bool:
        return any(token in lowered for token in family)

    def _is_question(self, lowered: str) -> bool:
        return lowered.endswith("?") or lowered.startswith((
            "qual ", "quais ", "como ", "por que", "porque ", "vale ",
            "devo ", "o que ", "quem ", "onde ", "quando ",
        ))

    def _is_technical_question(self, lowered: str) -> bool:
        return self._is_question(lowered) and any(obj in lowered for obj in self.TECH_OBJECTS)

    def _semantic_relational_topic(self, lowered: str) -> str:
        for topic, family in self.SEMANTIC_RELATIONAL_MAP.items():
            if any(token in lowered for token in family):
                return topic
        return ""

    def classify(self, user_text: str, memory=None) -> CognitiveDecision:
        lowered = user_text.lower().strip()

        if lowered in self.NEUTRAL_SHORTS:
            return CognitiveDecision(domain="neutral", query=user_text)

        semantic_topic = None
        if memory:
            semantic_topic = memory.detect_semantic_topic(user_text)

        if not semantic_topic:
            semantic_topic = self._semantic_relational_topic(lowered)
            if not semantic_topic and memory:
                semantic_topic = memory._semantic_emotion_topic(lowered)

        if self._starts(lowered, self.ACTION_DESKTOP):
            return CognitiveDecision(domain="action", capability="desktop", query=user_text)

        if self._starts(lowered, self.ACTION_FILE):
            return CognitiveDecision(domain="action", capability="file", query=user_text)

        if self._starts(lowered, self.FACTUAL_WEB):
            return CognitiveDecision(domain="factual", capability="web_search", query=user_text, is_question=True, has_external_knowledge=True)

        if self._contains(lowered, self.LOCAL_CODE_SEARCH):
            return CognitiveDecision(domain="practical", capability="local_search", query=user_text, is_question=True)

        if self._contains(lowered, self.PRACTICAL_MARKERS) or self._is_technical_question(lowered):
            return CognitiveDecision(domain="practical", capability="advisory", query=user_text, is_question=self._is_question(lowered))

        if self._contains(lowered, self.MEMORY_MARKERS):
            return CognitiveDecision(domain="memory_probe", query=user_text, is_question=True)

        if lowered.startswith(self.PERSONAL_FACT_PREFIXES):
            return CognitiveDecision(domain="personal", query=user_text, is_personal_statement=True)

        if semantic_topic:
            return CognitiveDecision(
                domain="semantic_relational",
                query=user_text,
                semantic_topic=semantic_topic,
                is_question=self._is_question(lowered),
            )

        if memory and memory._is_contextual_continuation(lowered):
            contextual = memory._contextual_semantic_topic(lowered) or memory.social_state.current_topic or "uncertainty"
            return CognitiveDecision(
                domain="semantic_relational",
                query=user_text,
                semantic_topic=contextual,
                is_question=self._is_question(lowered),
            )

        emotional_markers = (
            "sinto", "parece", "minha cabeça", "minha mente", "tem algo",
            "não consigo", "nao consigo", "estou", "tô", "to", "em mim",
            "não me", "nao me", "dentro de mim", "dentro de mim"
        )

        if any(marker in lowered for marker in emotional_markers):
            fallback_topic = memory._semantic_emotion_topic(lowered) if memory else None
            return CognitiveDecision(
                domain="semantic_relational",
                query=user_text,
                semantic_topic=fallback_topic or "uncertainty",
                is_question=self._is_question(lowered),
            )

        return CognitiveDecision(
            domain="neutral",
            query=user_text,
            semantic_topic="",
            is_question=self._is_question(lowered),
        )
