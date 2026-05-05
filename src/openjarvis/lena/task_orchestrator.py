from __future__ import annotations

from typing import Callable


class LenaTaskOrchestrator:
    CHAIN_CONNECTORS = (
        " e depois ",
        " depois ",
        " e então ",
        " e entao ",
        " e em seguida ",
    )

    KNOWN_PREFIXES = (
        "abre ",
        "abrir ",
        "fecha ",
        "fechar ",
        "google ",
        "pesquisa no google ",
        "pesquisar no google ",
        "busca no google ",
        "abre site ",
        "abrir site ",
        "abrir url ",
        "cria arquivo ",
        "criar arquivo ",
        "lê arquivo ",
        "le arquivo ",
        "lista arquivos ",
        "move arquivo ",
        "deleta arquivo ",
        "deletar arquivo ",
    )

    @classmethod
    def _detect_prefix(cls, part: str) -> str | None:
        lowered = part.lower()
        for prefix in cls.KNOWN_PREFIXES:
            if lowered.startswith(prefix):
                return prefix
        return None

    @classmethod
    def split(cls, user_text: str) -> list[str]:
        lowered = user_text.lower()
        if not any(connector in lowered for connector in cls.CHAIN_CONNECTORS):
            return [user_text]

        normalized = user_text
        for connector in cls.CHAIN_CONNECTORS:
            normalized = normalized.replace(connector, " || ")

        raw_parts = [part.strip(" ,.") for part in normalized.split(" || ") if part.strip(" ,.")]
        if not raw_parts:
            return [user_text]

        valid_parts: list[str] = []
        current_prefix: str | None = None

        for part in raw_parts:
            prefix = cls._detect_prefix(part)

            if prefix:
                current_prefix = prefix
                valid_parts.append(part)
                continue

            if current_prefix:
                valid_parts.append(current_prefix + part)
                continue

            return [user_text]

        return valid_parts if len(valid_parts) > 1 else [user_text]

    @staticmethod
    def execute(user_text: str, executor: Callable[[str], str]) -> str:
        commands = LenaTaskOrchestrator.split(user_text)
        outputs = [executor(command) for command in commands]
        return " | ".join(outputs)
