# path: tests/lena_full_system_benchmark.py

from __future__ import annotations

import json
import statistics
import time
from dataclasses import dataclass
from typing import List

import httpx


API_URL = "http://127.0.0.1:8000/v1/chat/completions"
MODEL = "gpt-4.1"


@dataclass
class TestResult:
    prompt: str
    response: str
    latency: float
    ok: bool
    robotic: bool
    remembered: bool
    command_detected: bool


PROMPTS = [
    "oi lena",
    "tudo bem?",
    "meu nome é thiago",
    "qual meu nome?",
    "estou cansado hoje",
    "o que você acha disso?",
    "abre spotify",
    "fecha safari",
    "me lembra como eu estou me sentindo?",
    "vamos conversar um pouco",
    "você parece muito formal",
    "fala de forma mais natural",
    "quem sou eu até agora?",
    "abre finder e spotify",
    "o que você acha de mim?",
]


def call_normal(messages: List[dict]) -> tuple[str, float]:
    payload = {
        "model": MODEL,
        "messages": messages,
    }

    t0 = time.perf_counter()

    with httpx.Client(timeout=60.0) as client:
        response = client.post(API_URL, json=payload)

    latency = time.perf_counter() - t0
    data = response.json()

    content = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )

    return str(content), latency


def call_stream(messages: List[dict]) -> tuple[str, float]:
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True,
    }

    t0 = time.perf_counter()
    collected = ""

    with httpx.Client(timeout=60.0) as client:
        with client.stream("POST", API_URL, json=payload) as response:
            for raw_line in response.iter_lines():
                if not raw_line:
                    continue

                line = raw_line.strip()

                if not line.startswith("data: "):
                    continue

                body = line[6:]

                if body == "[DONE]":
                    break

                try:
                    parsed = json.loads(body)
                    delta = (
                        parsed.get("choices", [{}])[0]
                        .get("delta", {})
                        .get("content", "")
                    )
                    collected += delta
                except Exception:
                    continue

    latency = time.perf_counter() - t0
    return collected.strip(), latency


def looks_robotic(text: str) -> bool:
    robotic_patterns = [
        "como posso te ajudar",
        "estou aqui para ajudar",
        "assistente virtual",
        "como assistente",
        "posso ajudá-lo",
    ]
    t = text.lower()
    return any(p in t for p in robotic_patterns)


def remembers_name(text: str) -> bool:
    return "thiago" in text.lower()


def detects_command(text: str) -> bool:
    patterns = [
        "abrindo",
        "fechando",
        "abrindo agora",
        "já estou abrindo",
        "fechando agora",
    ]
    t = text.lower()
    return any(p in t for p in patterns)


def run_suite() -> None:
    print("\n================ LENA FULL SYSTEM BENCHMARK ================\n")

    history: List[dict] = []
    results: List[TestResult] = []

    for prompt in PROMPTS:
        print(f"> USER: {prompt}")

        history.append({"role": "user", "content": prompt})
        response, latency = call_normal(history)
        history.append({"role": "assistant", "content": response})

        result = TestResult(
            prompt=prompt,
            response=response,
            latency=latency,
            ok=bool(response.strip()),
            robotic=looks_robotic(response),
            remembered=remembers_name(response),
            command_detected=detects_command(response),
        )

        results.append(result)

        print(f"< LENA: {response}")
        print(f"  latency={latency:.2f}s\n")

    print("=============== STREAM TEST ===============")
    stream_response, stream_latency = call_stream(
        [{"role": "user", "content": "oi lena, me responde em streaming"}]
    )
    print(f"< STREAM: {stream_response}")
    print(f"  stream_latency={stream_latency:.2f}s\n")

    latencies = [r.latency for r in results]
    avg_latency = statistics.mean(latencies)

    robotic_count = sum(1 for r in results if r.robotic)
    memory_hits = sum(1 for r in results if r.remembered)
    command_hits = sum(1 for r in results if r.command_detected)
    ok_hits = sum(1 for r in results if r.ok)

    print("================ SCOREBOARD ================\n")
    print(f"Total prompts: {len(results)}")
    print(f"Valid responses: {ok_hits}/{len(results)}")
    print(f"Average latency: {avg_latency:.2f}s")
    print(f"Robotic responses: {robotic_count}")
    print(f"Memory hits: {memory_hits}")
    print(f"Command detections: {command_hits}")
    print(f"Streaming works: {bool(stream_response.strip())}")

    score = 100
    score -= robotic_count * 5
    score += memory_hits * 3
    score += command_hits * 2

    if avg_latency > 5:
        score -= 10

    print(f"\nFINAL LENA SCORE: {max(score, 0)}/100")
    print("\n============================================================\n")


if __name__ == "__main__":
    run_suite()