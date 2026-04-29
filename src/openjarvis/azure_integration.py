# path: src/openjarvis/azure_integration.py

from __future__ import annotations

import re


def analisar_intencao(texto: str) -> str:
    lowered = texto.lower().strip()

    command_markers = [
        "abre ",
        "abrir ",
        "fecha ",
        "fechar ",
        "pesquisa ",
        "procura ",
        "google ",
        "https://",
        "http://",
    ]

    quick_markers = [
        "oi",
        "oi lena",
        "olá",
        "ola",
        "tudo bem",
    ]

    emotional_markers = [
        "estou triste",
        "estou cansado",
        "estou cansada",
        "estou desanimado",
        "estou desanimada",
        "estou meio desanimado",
        "estou meio desanimada",
        "sem vontade",
    ]

    reflective_markers = [
        "o que você acha",
        "me responde sinceramente",
        "você tá conseguindo me entender",
        "como você me percebe",
        "quem eu sou",
        "como eu estou",
    ]

    if any(lowered.startswith(marker) for marker in command_markers):
        return "comando"

    if any(lowered.startswith(marker) for marker in quick_markers):
        return "rapida"

    if any(marker in lowered for marker in emotional_markers):
        return "emocional"

    if any(marker in lowered for marker in reflective_markers):
        return "reflexiva"

    if re.search(r"\?$", lowered):
        return "curiosa"

    return "normal"