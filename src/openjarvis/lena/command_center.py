from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ParsedCommand:
    action: str
    targets: List[str]


class LenaCommandCenter:
    OPEN_WORDS = ["abre", "abrir", "open", "inicia", "iniciar"]
    CLOSE_WORDS = ["fecha", "fechar", "close", "encerra", "encerrar"]
    SEARCH_WORDS = ["pesquisa no google", "procura no google", "buscar no google", "pesquisa", "google"]

    @classmethod
    def parse(cls, text: str) -> Optional[ParsedCommand]:
        normalized = text.lower().strip()

        if re.match(r"^https?://", normalized):
            return ParsedCommand(action="url", targets=[normalized])

        if cls._contains_any(normalized, cls.OPEN_WORDS):
            apps = cls._extract_targets(normalized, cls.OPEN_WORDS)
            if apps:
                return ParsedCommand(action="open", targets=apps)

        if cls._contains_any(normalized, cls.CLOSE_WORDS):
            apps = cls._extract_targets(normalized, cls.CLOSE_WORDS)
            if apps:
                return ParsedCommand(action="close", targets=apps)

        if cls._contains_any(normalized, cls.SEARCH_WORDS):
            query = cls._extract_search_query(normalized)
            if query:
                return ParsedCommand(action="search", targets=[query])

        return None

    @staticmethod
    def _contains_any(text: str, words: List[str]) -> bool:
        return any(word in text for word in words)

    @staticmethod
    def _extract_targets(text: str, verbs: List[str]) -> List[str]:
        cleaned = text

        for verb in verbs:
            cleaned = cleaned.replace(verb, "")

        cleaned = cleaned.replace(" e ", ",")
        cleaned = cleaned.replace(" and ", ",")
        cleaned = cleaned.replace(" também ", ",")
        cleaned = cleaned.replace(" tambem ", ",")

        parts = [part.strip() for part in cleaned.split(",") if part.strip()]
        return parts

    @staticmethod
    def _extract_search_query(text: str) -> str:
        text = re.sub(r"pesquisa no google", "", text)
        text = re.sub(r"procura no google", "", text)
        text = re.sub(r"buscar no google", "", text)
        text = re.sub(r"pesquisa", "", text)
        text = re.sub(r"google", "", text)
        return text.strip()