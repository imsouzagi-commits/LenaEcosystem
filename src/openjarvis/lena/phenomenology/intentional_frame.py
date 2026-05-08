from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class IntentionalFrame:

    type: str

    confidence: float


class IntentionalFrameResolver:

    WORLDLY_MARKERS = {
        "filme",
        "filmes",
        "música",
        "musica",
        "banda",
        "bandas",
        "clima",
        "tempo",
        "comida",
        "jogo",
        "jogos",
        "anime",
        "livro",
        "livros",
        "série",
        "serie",
    }

    EXPLORATORY_MARKERS = {
        "como",
        "por que",
        "porque",
        "qual",
        "quais",
        "o que",
        "quem",
    }

    RELATIONAL_MARKERS = {
        "oi",
        "olá",
        "ola",
        "bom dia",
        "boa tarde",
        "boa noite",
        "obrigado",
        "valeu",
    }

    DISPLACEMENT_MARKERS = {
        "muda de assunto",
        "vamos falar de outra coisa",
        "troca de assunto",
        "quero mudar de assunto",
    }

    INTERNAL_MARKERS = {
        "não consigo",
        "nao consigo",
        "continua",
        "volta",
        "peso",
        "cansado",
        "drenado",
        "ansiedade",
        "cabeça",
        "cabeca",
        "mente",
    }

    @classmethod
    def resolve(
        cls,
        text: str,
    ) -> IntentionalFrame:

        lowered = text.lower().strip()

        for marker in cls.DISPLACEMENT_MARKERS:

            if marker in lowered:
                return IntentionalFrame(
                    type="displacement",
                    confidence=0.95,
                )

        for marker in cls.WORLDLY_MARKERS:

            if marker in lowered:
                return IntentionalFrame(
                    type="worldly",
                    confidence=0.90,
                )

        for marker in cls.RELATIONAL_MARKERS:

            if marker in lowered:
                return IntentionalFrame(
                    type="relational",
                    confidence=0.75,
                )

        for marker in cls.INTERNAL_MARKERS:

            if marker in lowered:
                return IntentionalFrame(
                    type="internal",
                    confidence=0.85,
                )

        for marker in cls.EXPLORATORY_MARKERS:

            if marker in lowered:
                return IntentionalFrame(
                    type="exploratory",
                    confidence=0.70,
                )

        return IntentionalFrame(
            type="internal",
            confidence=0.40,
        )
