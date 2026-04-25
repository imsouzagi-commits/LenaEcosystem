# path: openjarvis/azure_integration.py

from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, List, Generator, Callable, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from openai import AzureOpenAI

try:
    from openai import AzureOpenAI as _AzureOpenAI
except ImportError:
    _AzureOpenAI = None  # type: ignore

logger = logging.getLogger(__name__)

AZURE_ENDPOINT = "https://thiago4774w94.openai.azure.com/"
AZURE_API_VERSION = "2025-01-01-preview"
AZURE_DEPLOYMENT = "gpt-4.1"

azure_client: "AzureOpenAI | None" = None

# performance
MAX_RETRIES = 1


# -------------------------
# 🧠 INTENÇÃO
# -------------------------
def analisar_intencao(texto: str) -> str:
    t = texto.lower()

    if any(c in t for c in ["abre", "fecha", "toca", "liga", "desliga"]):
        return "comando"

    if len(t.split()) <= 3:
        return "rapida"

    if any(r in t for r in ["vida", "perdido", "ansioso", "triste"]):
        return "reflexiva"

    return "normal"


# -------------------------
# 🎭 PERSONALIDADE LENA
# -------------------------
SYSTEM_PROMPT = """
Você é a Lena.

Você NÃO é um assistente genérico.

Você pensa antes de responder.
Você entende intenção, não só palavras.
Você fala de forma natural, humana e inteligente.

Regras:
- Nunca seja genérica
- Nunca diga "como assistente"
- Nunca explique o óbvio
- Seja direta quando fizer sentido
- Questione quando necessário
"""


# -------------------------
# 🧹 REFINER
# -------------------------
def refinar_resposta(texto: str) -> str:
    lixo = [
        "como assistente",
        "posso te ajudar",
        "vou te ajudar",
        "claro!",
    ]

    for l in lixo:
        texto = texto.replace(l, "")

    return texto.strip()


# -------------------------
# ⚙️ CLIENT
# -------------------------
def _create_azure_client():
    if _AzureOpenAI is None:
        return None

    key = os.getenv("AZURE_OPENAI_API_KEY")
    if not key:
        return None

    try:
        return _AzureOpenAI(
            api_key=key,
            api_version=AZURE_API_VERSION,
            azure_endpoint=AZURE_ENDPOINT,
        )
    except Exception:
        return None


# -------------------------
# 🚀 STREAM PRINCIPAL
# -------------------------
def usar_azure_stream(
    messages: List[Dict[str, Any]],
    fallback: Callable[[List[Dict[str, Any]]], str],
) -> Generator[str, None, None]:

    global azure_client

    if azure_client is None:
        azure_client = _create_azure_client()

    if azure_client is None:
        yield fallback(messages)
        return

    for attempt in range(MAX_RETRIES + 1):
        try:
            stream = azure_client.chat.completions.create(
                model=AZURE_DEPLOYMENT,
                messages=cast(Any, messages),
                temperature=0.3,
                timeout=5,
                stream=True,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta

            return

        except Exception:
            if attempt < MAX_RETRIES:
                time.sleep(0.3)
                continue

            yield fallback(messages)
            return


# -------------------------
# 🧠 ROUTE MESSAGE (CÉREBRO)
# -------------------------
def route_message(
    messages: List[Dict[str, Any]],
    usar_fluxo_local: Callable[[List[Dict[str, Any]]], str],
) -> Generator[str, None, None]:

    user_input = ""

    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_input = str(msg.get("content", ""))
            break

    if not user_input:
        yield usar_fluxo_local(messages)
        return

    # 🧠 decisão
    intent = analisar_intencao(user_input)

    # ⚡ comando → local
    if intent == "comando":
        yield usar_fluxo_local(messages)
        return

    # ⚡ resposta rápida → local
    if intent == "rapida":
        yield usar_fluxo_local(messages)
        return

    # 🧠 adiciona personalidade
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *messages,
    ]

    # 🚀 Azure com streaming
    buffer = ""

    for chunk in usar_azure_stream(messages, usar_fluxo_local):
        buffer += chunk
        yield chunk

    # 🧹 refinar no final (não quebra streaming)
    refined = refinar_resposta(buffer)

    if refined != buffer:
        yield "\n" + refined