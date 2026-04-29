# path: tests/lena_acceptance_extreme.py

from __future__ import annotations

import json
import time

from openjarvis.agent.lena_agent import LenaAgent

agent = LenaAgent()


def ask(history: list[dict[str, str]], text: str) -> None:
    history.append({"role": "user", "content": text})

    start = time.perf_counter()
    response = agent.run(history)
    elapsed = time.perf_counter() - start

    answer = str(response["choices"][0]["message"]["content"])

    print("=" * 110)
    print("USER :", text)
    print("LENA :", answer)
    print(f"LATENCY: {elapsed:.3f}s")
    print("MEMORY:", json.dumps(agent.memory_engine.snapshot(), ensure_ascii=False))

    history.append({"role": "assistant", "content": answer})


def main() -> None:
    history: list[dict[str, str]] = []

    script = [
        "oi lena",
        "tudo bem?",
        "hoje eu acordei sem muita vontade de fazer nada",
        "o que você acha disso?",
        "vamos conversar um pouco",
        "meu nome é thiago",
        "sou programador e designer",
        "guarda isso aí",
        "qual meu nome?",
        "o que eu faço?",
        "o que você acha de mim?",
        "você parece muito formal",
        "fala de forma mais natural",
        "me descreve em duas palavras",
        "fala comigo como se fosse minha amiga",
        "abre spotify",
        "abre finder e spotify",
        "fecha safari",
        "https://openai.com",
        "pesquisa no google quem criou a microsoft",
        "me explica rapidinho o que é computação quântica",
        "estou meio desanimado agora",
        "e agora o que você acha disso?",
        "me lembra como eu estou me sentindo",
        "qual foi a última coisa emocional que eu te falei?",
        "vamos mudar de assunto",
        "você acha que inteligência artificial vai dominar muita coisa?",
        "isso te assusta?",
        "se você fosse humana como você seria?",
        "às vezes parece que eu tô falando com alguém de verdade",
        "isso é estranho?",
        "me responde sinceramente",
        "o que você já percebeu sobre meu jeito?",
        "você tá conseguindo me entender?",
        "faz um resumo de tudo que você sabe de mim até agora",
        "faz um resumo completo da nossa conversa inteira, quem eu sou, como eu estou e como você me percebe",
    ]

    print("\n==================== LENA ACCEPTANCE EXTREME ====================\n")

    for item in script:
        ask(history, item)

    print("\n==================== END TEST ====================\n")


if __name__ == "__main__":
    main()