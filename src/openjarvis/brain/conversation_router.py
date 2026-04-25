# path: openjarvis/brain/conversation_router.py

from typing import List, Dict, Any

from openjarvis.azure_integration import (
    analisar_intencao,
    refinar_resposta,
)
from openjarvis.engine.cloud import CloudEngine
from openjarvis.learning.routing.router import (
    HeuristicRouter,
    build_routing_context,
)

# -------- ENGINE --------
engine = CloudEngine()
model_router = HeuristicRouter()


# -------- PERSONALIDADE --------
SYSTEM_PROMPT = """
Você é Lena.

Você não responde automaticamente.
Você interpreta antes de falar.

Regras:
- Nunca seja genérica
- Nunca repita respostas
- Se a pergunta for vaga → questione
- Se for emocional → aprofunde
- Se for simples → responda curto

Você fala como uma pessoa real.
Natural, direta, às vezes levemente provocativa.
"""


# -------- ENTRYPOINT --------
def chat(messages: List[Dict[str, Any]]) -> str:
    user_input = _last_user(messages)

    if not user_input:
        return "..."

    # 🧠 intenção
    intent = analisar_intencao(user_input)

    # ⚡ respostas locais (rápidas/comando)
    if intent in ["comando", "rapida"]:
        return _local_response(user_input)

    # 🎯 escolher modelo
    routing_context = build_routing_context(user_input)
    model = model_router.select_model(routing_context)

    # 🧠 pensamento interno
    thought = _think(user_input, messages)

    # 🧱 contexto final
    context = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Pensamento interno: {thought}"},
        *messages[-8:],  # mantém contexto curto
    ]

    # 🚀 geração
    try:
        resp = engine.generate(
            messages=context,
            model=model or "gpt-4.1",
            temperature=0.85,
            max_tokens=400,
        )

        final = refinar_resposta(resp.get("content", ""))

        return final or "..."

    except Exception:
        return "Hmm... deu algo estranho aqui. Tenta de novo."


# -------- HELPERS --------

def _last_user(messages: List[Dict[str, Any]]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            return str(m.get("content", ""))
    return ""


def _think(user_input: str, messages: List[Dict[str, Any]]) -> str:
    return f"""
Usuário disse: {user_input}

Contexto recente: {messages[-4:]}

O que ele realmente quer?
"""


def _local_response(user_input: str) -> str:
    t = user_input.lower()

    if "oi" in t:
        return "Oi. Fala direto, o que você quer?"

    if "tudo bem" in t:
        return "Depende. E você?"

    if "abre" in t or "fecha" in t:
        return "Ok, isso parece um comando. Me dá mais detalhe."

    return "Hmm. Explica melhor."