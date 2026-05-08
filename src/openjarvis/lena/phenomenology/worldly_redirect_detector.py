from __future__ import annotations


class WorldlyRedirectDetector:

    TOKENS = {
        "música",
        "musica",
        "filme",
        "filmes",
        "banda",
        "bandas",
        "clima",
        "tempo",
        "comida",
        "série",
        "serie",
        "jogo",
        "jogos",
        "livro",
        "livros",
        "anime",
        "hobby",
    }

    @classmethod
    def detect(
        cls,
        text: str,
    ) -> bool:

        lowered = text.lower()

        for token in cls.TOKENS:

            if token in lowered:
                return True

        return False
