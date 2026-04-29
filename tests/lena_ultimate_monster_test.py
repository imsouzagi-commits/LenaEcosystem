# tests/lena_ultimate_monster_test.py

from __future__ import annotations

import time
from typing import Any, Dict, List

from openjarvis.agent.lena_agent import LenaAgent


def ask(agent: LenaAgent, conversation: List[Dict[str, Any]], text: str) -> None:
    start = time.perf_counter()

    conversation.append({"role": "user", "content": text})
    result = agent.run(conversation)

    latency = time.perf_counter() - start
    answer = result["choices"][0]["message"]["content"]

    print("\n" + "=" * 110)
    print("USER :", text)
    print("LENA :", answer)
    print(f"LATENCY: {latency:.3f}s")

    conversation.append({"role": "assistant", "content": answer})


def ask_stream(agent: LenaAgent, conversation: List[Dict[str, Any]], text: str) -> None:
    start = time.perf_counter()

    conversation.append({"role": "user", "content": text})

    print("\n" + "=" * 110)
    print("USER :", text)
    print("LENA STREAM:", end=" ", flush=True)

    collected = ""

    for chunk in agent.run_stream(conversation):
        print(chunk, end="", flush=True)
        collected += chunk

    latency = time.perf_counter() - start
    print(f"\nLATENCY STREAM: {latency:.3f}s")

    conversation.append({"role": "assistant", "content": collected})


def main() -> None:
    agent = LenaAgent()
    conversation: List[Dict[str, Any]] = []

    print("\n==================== LENA ULTIMATE MONSTER TEST ====================\n")

    # BLOCO 1 — SAUDAÇÃO + HUMANO
    ask(agent, conversation, "oi lena")
    ask(agent, conversation, "tudo bem?")
    ask(agent, conversation, "hoje eu acordei sem muita vontade de fazer nada")
    ask(agent, conversation, "o que você acha disso?")
    ask(agent, conversation, "vamos conversar um pouco")

    # BLOCO 2 — MEMÓRIA IDENTIDADE
    ask(agent, conversation, "meu nome é thiago")
    ask(agent, conversation, "sou programador e designer")
    ask(agent, conversation, "guarda isso aí")
    ask(agent, conversation, "qual meu nome?")
    ask(agent, conversation, "o que eu faço?")
    ask(agent, conversation, "o que você acha de mim?")

    # BLOCO 3 — AJUSTE DE PERSONALIDADE
    ask(agent, conversation, "você parece muito formal")
    ask(agent, conversation, "fala de forma mais natural")
    ask(agent, conversation, "me descreve em duas palavras")
    ask(agent, conversation, "fala comigo como se fosse minha amiga")

    # BLOCO 4 — COMANDOS NATIVOS
    ask(agent, conversation, "abre spotify")
    ask(agent, conversation, "abre finder e spotify")
    ask(agent, conversation, "fecha safari")
    ask(agent, conversation, "fecha chrome")

    # BLOCO 5 — URL + TOOL
    ask(agent, conversation, "https://openai.com")
    ask(agent, conversation, "https://google.com")
    ask(agent, conversation, "https://github.com")

    # BLOCO 6 — PESQUISA
    ask(agent, conversation, "pesquisa no google quem criou a microsoft")
    ask(agent, conversation, "pesquisa no google clima em nova york")
    ask(agent, conversation, "pesquisa no google últimas notícias sobre inteligência artificial")

    # BLOCO 7 — CONHECIMENTO COMPLEXO
    ask(agent, conversation, "me explica rapidinho o que é computação quântica")
    ask(agent, conversation, "qual a diferença entre ia generativa e ia tradicional")
    ask(agent, conversation, "quem criou a teoria da relatividade")
    ask(agent, conversation, "crie uma estratégia de marketing para uma cafeteria pequena")

    # BLOCO 8 — MEMÓRIA EMOCIONAL
    ask(agent, conversation, "estou meio desanimado agora")
    ask(agent, conversation, "e agora o que você acha disso?")
    ask(agent, conversation, "me lembra como eu estou me sentindo")
    ask(agent, conversation, "qual foi a última coisa emocional que eu te falei?")

    # BLOCO 9 — RESENHA LONGA
    ask(agent, conversation, "vamos mudar de assunto")
    ask(agent, conversation, "você acha que inteligência artificial vai dominar muita coisa?")
    ask(agent, conversation, "isso te assusta?")
    ask(agent, conversation, "se você fosse humana como você seria?")
    ask(agent, conversation, "às vezes parece que eu tô falando com alguém de verdade")
    ask(agent, conversation, "isso é estranho?")
    ask(agent, conversation, "me responde sinceramente")

    # BLOCO 10 — MEMÓRIA CRUZADA
    ask(agent, conversation, "o que você já percebeu sobre meu jeito?")
    ask(agent, conversation, "você tá conseguindo me entender?")
    ask(agent, conversation, "faz um resumo de tudo que você sabe de mim até agora")

    # BLOCO 11 — STREAM FINAL
    ask_stream(
        agent,
        conversation,
        "faz um resumo completo da nossa conversa inteira, quem eu sou, como eu estou e como você me percebe",
    )

    print("\n==================== END OF MONSTER TEST ====================\n")


if __name__ == "__main__":
    main()