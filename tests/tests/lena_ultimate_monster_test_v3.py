from __future__ import annotations

import json
import time
from collections import Counter

from openjarvis.agent.lena_agent import LenaAgent


def classify_route(answer: str, latency: float) -> str:
    if answer.startswith(("Abrindo", "Fechando", "Pesquisando")):
        if "Pesquisando" in answer:
            return "WEB_SEARCH"
        if "http" in answer:
            return "TOOL"
        return "COMMAND"

    if latency < 0.03:
        return "FAST_OR_MEMORY"

    if latency < 0.30:
        return "MEMORY_OR_LOCAL"

    return "CLOUD"


def ask(agent: LenaAgent, history: list[dict], prompt: str, route_counter: Counter, latencies: list[float]) -> None:
    history.append({"role": "user", "content": prompt})

    t0 = time.perf_counter()
    result = agent.run(history)
    latency = time.perf_counter() - t0

    answer = result["choices"][0]["message"]["content"]
    route = classify_route(answer, latency)

    route_counter[route] += 1
    latencies.append(latency)

    print("\n" + "=" * 120)
    print("USER :", prompt)
    print("LENA :", answer)
    print(f"LATENCY: {latency:.3f}s")
    print(f"ROUTE: {route}")
    print("MEMORY:", json.dumps(agent.memory_engine.snapshot(), ensure_ascii=False))

    history.append({"role": "assistant", "content": answer})


def ask_stream(agent: LenaAgent, history: list[dict], prompt: str, route_counter: Counter, latencies: list[float]) -> None:
    history.append({"role": "user", "content": prompt})

    t0 = time.perf_counter()
    chunks: list[str] = []

    print("\n" + "=" * 120)
    print("USER :", prompt)
    print("LENA STREAM:", end=" ")

    for chunk in agent.run_stream(history):
        print(chunk, end="", flush=True)
        chunks.append(chunk)

    latency = time.perf_counter() - t0
    final_answer = "".join(chunks).strip()
    route = classify_route(final_answer, latency)

    route_counter[route] += 1
    latencies.append(latency)

    print(f"\nLATENCY STREAM: {latency:.3f}s")
    print(f"ROUTE STREAM: {route}")
    print("MEMORY:", json.dumps(agent.memory_engine.snapshot(), ensure_ascii=False))

    history.append({"role": "assistant", "content": final_answer})


def main() -> None:
    agent = LenaAgent()
    history: list[dict] = []
    route_counter: Counter = Counter()
    latencies: list[float] = []

    prompts = [
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
        "fecha chrome",
        "https://openai.com",
        "https://google.com",
        "https://github.com",
        "pesquisa no google quem criou a microsoft",
        "pesquisa no google clima em nova york",
        "pesquisa no google últimas notícias sobre inteligência artificial",
        "me explica rapidinho o que é computação quântica",
        "qual a diferença entre ia generativa e ia tradicional",
        "quem criou a teoria da relatividade",
        "crie uma estratégia de marketing para uma cafeteria pequena",
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
    ]

    print("\n==================== LENA ULTIMATE MONSTER TEST V3 ====================\n")

    for prompt in prompts:
        ask(agent, history, prompt, route_counter, latencies)

    ask_stream(
        agent,
        history,
        "faz um resumo completo da nossa conversa inteira, quem eu sou, como eu estou e como você me percebe",
        route_counter,
        latencies,
    )

    print("\n" + "=" * 110)
    print("LENA PERFORMANCE SCORE REPORT")
    print("=" * 110)
    print(f"TOTAL TESTS: {len(prompts) + 1}")
    print()

    for route, count in sorted(route_counter.items()):
        print(f"{route}: {count}")

    print()
    print(f"AVG LATENCY: {sum(latencies) / len(latencies):.3f}s")
    print(f"MAX LATENCY: {max(latencies):.3f}s")
    print("=" * 110)
    print("\n==================== END OF MONSTER TEST V3 ====================\n")


if __name__ == "__main__":
    main()