# path: tests/lena_e2e_runner.py

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import List, Tuple

import requests

API_URL = "http://127.0.0.1:8000/v1/chat/completions/fallback"
MODEL = "gpt-4.1"


@dataclass
class TestResult:
    category: str
    prompt: str
    success: bool
    latency: float
    response: str
    details: str = ""


class LenaE2ERunner:
    def __init__(self) -> None:
        self.results: List[TestResult] = []

    def _post(self, message: str, stream: bool = False) -> Tuple[str, float]:
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": message}],
            "temperature": 0.35,
            "max_tokens": 400,
            "stream": stream,
        }

        t0 = time.time()
        resp = requests.post(API_URL, json=payload, timeout=40, stream=stream)
        latency = time.time() - t0

        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")

        if not stream:
            data = resp.json()
            content = str(data["choices"][0]["message"]["content"])
            return content, latency

        chunks: List[str] = []

        for raw in resp.iter_lines():
            if not raw:
                continue

            line = raw.decode()

            if line.strip() == "data: [DONE]":
                break

            if not line.startswith("data: "):
                continue

            payload_raw = line[6:]

            try:
                event = json.loads(payload_raw)
                delta = event["choices"][0]["delta"].get("content")
                if delta:
                    chunks.append(str(delta))
            except Exception:
                continue

        return "".join(chunks), latency

    def _evaluate_human_quality(self, text: str) -> tuple[bool, str]:
        lowered = text.lower()

        robotic_flags = [
            "como assistente",
            "posso te ajudar",
            "sou uma ia",
            "assistente virtual",
            "fico feliz em ajudar",
        ]

        if any(flag in lowered for flag in robotic_flags):
            return False, "resposta robótica"

        if len(text.strip()) < 2:
            return False, "resposta vazia"

        return True, "ok"

    def run_case(self, category: str, prompt: str, stream: bool = False) -> None:
        try:
            response, latency = self._post(prompt, stream=stream)
            ok, details = self._evaluate_human_quality(response)

            self.results.append(
                TestResult(
                    category=category,
                    prompt=prompt,
                    success=ok,
                    latency=float(latency),
                    response=response,
                    details=details,
                )
            )

        except Exception as exc:
            self.results.append(
                TestResult(
                    category=category,
                    prompt=prompt,
                    success=False,
                    latency=0.0,
                    response="",
                    details=str(exc),
                )
            )

    def run_all(self) -> None:
        simple_chat = [
            "oi lena",
            "quem é você?",
            "vamos conversar um pouco",
        ]

        memory_chat = [
            "meu nome é thiago",
            "qual meu nome?",
            "eu gosto de música eletrônica",
            "do que eu gosto?",
        ]

        emotional_chat = [
            "estou me sentindo sozinho hoje",
            "acho que estou cansado mentalmente",
        ]

        local_commands = [
            "abre spotify",
            "fecha safari",
            "aumenta volume",
        ]

        for msg in simple_chat:
            self.run_case("simple_chat", msg)

        for msg in memory_chat:
            self.run_case("memory", msg)

        for msg in emotional_chat:
            self.run_case("emotional", msg)

        for msg in local_commands:
            self.run_case("local_command", msg)

        self.run_case("streaming", "me conta algo interessante", stream=True)

    def print_report(self) -> None:
        print("\n" + "=" * 100)
        print("LENA E2E TEST REPORT")
        print("=" * 100)

        passed = 0

        for r in self.results:
            status = "PASS" if r.success else "FAIL"

            if r.success:
                passed += 1

            print(f"\n[{status}] {r.category}")
            print(f"Prompt   : {r.prompt}")
            print(f"Latency  : {r.latency:.2f}s")
            print(f"Details  : {r.details}")
            print(f"Response : {r.response[:300]}")

        print("\n" + "=" * 100)
        print(f"TOTAL: {passed}/{len(self.results)} passed")
        print("=" * 100)


if __name__ == "__main__":
    runner = LenaE2ERunner()
    runner.run_all()
    runner.print_report()