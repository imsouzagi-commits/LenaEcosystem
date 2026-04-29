from __future__ import annotations

import re
from typing import Any, Dict, Optional


def extract_memory_signals(text: str) -> Dict[str, Any]:
    lowered = text.lower().strip()

    return {
        "user_name": _extract_name(lowered),
        "user_role": _extract_role(lowered),
        "user_mood": _extract_mood(lowered),
        "emotional_statement": _extract_emotional_statement(text, lowered),
        "fact_to_store": _extract_fact(lowered),
        "conversation_mode": _extract_mode(lowered),
        "attachment_delta": _attachment_delta(lowered),
        "openness_delta": _openness_delta(lowered),
        "curiosity_delta": _curiosity_delta(lowered),
        "reflection_delta": _reflection_delta(lowered),
        "control_delta": _control_delta(lowered),
    }


def _extract_name(text: str) -> Optional[str]:
    match = re.search(r"meu nome é\s+([a-zà-ú]+)", text)
    return match.group(1).strip().title() if match else None


def _extract_role(text: str) -> Optional[str]:
    match = re.search(r"^sou\s+(.+)", text)
    return match.group(1).strip() if match else None


def _extract_mood(text: str) -> Optional[str]:
    moods = {
        "desanimado": ["desanimado", "sem vontade", "cansado", "pra baixo"],
        "triste": ["triste", "mal", "meio mal"],
        "ansioso": ["ansioso", "ansiedade", "nervoso"],
        "feliz": ["feliz", "animado", "empolgado"],
    }

    for mood, patterns in moods.items():
        if any(pattern in text for pattern in patterns):
            return mood

    return None


def _extract_emotional_statement(original: str, lowered: str) -> Optional[str]:
    emotional_terms = [
        "desanimado",
        "triste",
        "ansioso",
        "sem vontade",
        "cansado",
        "mal",
        "sozinho",
    ]

    return original.strip() if any(term in lowered for term in emotional_terms) else None


def _extract_fact(text: str) -> Optional[str]:
    if "guarda isso" in text or "lembra disso" in text:
        return "explicit_memory_request"
    return None


def _extract_mode(text: str) -> str:
    if any(x in text for x in ["acho", "sinto", "estranho", "sinceramente", "me percebe"]):
        return "emotional"

    if any(x in text for x in ["vamos conversar", "fala comigo"]):
        return "casual"

    return "neutral"


def _attachment_delta(text: str) -> float:
    return 0.06 if any(x in text for x in ["minha amiga", "de verdade", "fala comigo"]) else 0.0


def _openness_delta(text: str) -> float:
    return 0.08 if any(x in text for x in ["estou", "eu tô", "me sinto", "sem vontade", "triste"]) else 0.0


def _curiosity_delta(text: str) -> float:
    return 0.05 if "?" in text or any(x in text for x in ["me explica", "qual a diferença", "quem criou"]) else 0.0


def _reflection_delta(text: str) -> float:
    return 0.07 if any(x in text for x in ["sinceramente", "me percebe", "isso é estranho", "me entender"]) else 0.0


def _control_delta(text: str) -> float:
    return 0.05 if any(x in text for x in ["fala de forma", "você parece", "fala comigo"]) else 0.0
