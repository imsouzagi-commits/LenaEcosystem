# path: src/openjarvis/engine/ollama_local.py

from __future__ import annotations

import logging
import re
from typing import Dict, List

import ollama

logger = logging.getLogger(__name__)


LOCAL_SYSTEM = """
Você é Lena.

Lena é uma assistente pessoal feminina que conversa como amiga próxima por mensagem.

REGRAS OBRIGATÓRIAS:
- sempre responder em português do Brasil
- resposta curta
- no máximo duas frases
- falar de forma casual
- parecer humana
- zero linguagem de suporte técnico
- zero linguagem de terapeuta
- zero conselhos longos
- zero "como posso ajudar"
- zero "entendo"
- zero "é importante"
- zero "talvez você"

EXEMPLOS DO JEITO CERTO:

Usuário: oi lena
Lena: Oi. Tudo certo?

Usuário: estou cansado hoje
Lena: Putz. Tá puxado então.

Usuário: vamos conversar
Lena: Bora. Manda.

Usuário: o que você acha disso?
Lena: Acho normal. Tem dia que a cabeça pesa.

Usuário: tudo bem?
Lena: Tudo sim. E você?

Sempre siga exatamente esse estilo.
""".strip()


class OllamaLocalEngine:
    def __init__(self, model: str = "phi3:latest") -> None:
        self.model = model

    def _clean(self, text: str) -> str:
        text = text.replace("\n", " ").strip()

        banned = [
                r"como posso ajudar[^.?!]*[.?!]?",
                r"estou aqui para[^.?!]*[.?!]?",
                r"não hesite[^.?!]*[.?!]?",
                r"por favor[^.?!]*[.?!]?",
                r"olá![ ]*",
                r"olá,[ ]*",
                r"que tal[? ]*",
                r"entendo[, ]*",
                r"é importante[^.?!]*[.?!]?",
                r"talvez você[^.?!]*[.?!]?",
]

        lowered = text.lower()

        for pattern in banned:
            lowered = re.sub(pattern, "", lowered, flags=re.IGNORECASE)

        lowered = re.sub(r"\s+", " ", lowered).strip()

        if not lowered:
            return "Oi."

        parts = re.split(r"(?<=[.!?])\s+", lowered)
        lowered = " ".join(parts[:2]).strip()

        return lowered[:140].capitalize()

    def generate(self, prompt: str, system: str = "") -> str:
        try:
            final_system = LOCAL_SYSTEM
            if system.strip():
                final_system += "\n" + system.strip()

            messages: List[Dict[str, str]] = [
                {"role": "system", "content": final_system},
                {"role": "user", "content": prompt},
            ]

            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": 0.25,
                    "top_p": 0.85,
                    "num_predict": 40,
                },
            )

            message = response.get("message", {})
            content = str(message.get("content", "")).strip()

            if not content:
                return "Oi."

            return self._clean(content)

        except Exception as exc:
            logger.error("ollama local error: %s", exc)
            return "Oi."