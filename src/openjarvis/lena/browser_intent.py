from __future__ import annotations


class LenaBrowserIntent:
    SEARCH_PREFIXES = (
        "pesquisa ",
        "pesquisa no google ",
        "procura ",
        "busca ",
        "google ",
    )

    @classmethod
    def is_search_intent(cls, user_text: str) -> bool:
        lowered = user_text.lower().strip()
        return any(lowered.startswith(prefix) for prefix in cls.SEARCH_PREFIXES)

    @classmethod
    def extract_query(cls, user_text: str) -> str:
        lowered = user_text.lower().strip()

        for prefix in cls.SEARCH_PREFIXES:
            if lowered.startswith(prefix):
                return user_text[len(prefix):].strip()

        return user_text.strip()
