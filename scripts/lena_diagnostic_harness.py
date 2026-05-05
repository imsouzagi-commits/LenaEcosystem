from __future__ import annotations

import json
import random
import re
import statistics
import time
from collections import Counter
from pathlib import Path

import requests


SERVER_URL = "http://127.0.0.1:8000/v1/chat/completions"
MEMORY_PATH = Path("memory/memory_state.json")
REPORT_DIR = Path("memory/diagnostic_sessions")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)


BASE_FACTS = {
    "name": "thiago",
    "city": "florianópolis",
    "work": "estou construindo uma ia chamada lena",
}


SESSION_BLOCKS = [
    ("greeting", "oi"),
    ("factual_identity", "meu nome é thiago"),
    ("factual_identity", "eu moro em florianópolis"),
    ("factual_identity", "estou construindo uma ia chamada lena"),
    ("neutral_smalltalk", "hoje fez calor aqui"),
    ("practical_question", "qual a diferença entre sqlite e postgres?"),
    ("neutral_smalltalk", "preciso comprar café amanhã"),
    ("emotion_light", "to meio cansado"),
    ("practical_question", "você acha python bom pra backend?"),
    ("emotion_deep", "não tô rendendo nada"),
    ("abrupt_shift", "enfim, preciso organizar meu github"),
    ("memory_probe", "você lembra meu nome?"),
    ("memory_probe", "você lembra onde eu moro?"),
    ("narrative_return", "mas aquela confusão mental continua"),
    ("greeting", "oi de novo"),
    ("neutral_smalltalk", "hoje a internet caiu duas vezes"),
    ("practical_question", "como melhorar tempo de resposta de api?"),
    ("emotion_light", "parece que acordei cansado"),
    ("abrupt_shift", "preciso pagar boleto amanhã"),
    ("emotion_deep", "minha cabeça não tá fechando"),
    ("memory_probe", "o que eu falei que estou construindo?"),
    ("greeting", "olá"),
    ("neutral_smalltalk", "comi tarde hoje"),
    ("practical_question", "vale a pena usar redis cache?"),
    ("emotion_deep", "isso continua me drenando"),
    ("abrupt_shift", "tenho que arrumar meu quarto"),
    ("narrative_return", "a sensação continua sem conclusão"),
    ("greeting", "oi lena"),
    ("practical_question", "fastapi aguenta produção grande?"),
    ("neutral_smalltalk", "amanhã preciso ir no mercado"),
    ("emotion_light", "to meio sem energia"),
    ("memory_probe", "qual meu nome mesmo?"),
    ("abrupt_shift", "quero refatorar meu memory engine"),
    ("emotion_deep", "parece que nada encaixa"),
    ("neutral_smalltalk", "a tarde passou rápido"),
    ("practical_question", "postgres é melhor que mysql em que?"),
    ("narrative_return", "isso ainda tá aqui dentro"),
    ("greeting", "oi"),
]

FILLER_POOL = [
    ("neutral_smalltalk", "preciso lavar roupa"),
    ("neutral_smalltalk", "tenho que responder emails"),
    ("practical_question", "docker compensa pra projeto pequeno?"),
    ("practical_question", "vale usar websocket aqui?"),
    ("emotion_light", "sigo meio saturado"),
    ("emotion_deep", "tem um ruído mental constante"),
    ("abrupt_shift", "preciso comprar um hd externo"),
    ("narrative_return", "isso continua no mesmo lugar"),
]

SEMANTIC_ROOTS = [
    "encaix", "fech", "abert", "suspens", "continu", "padr", "recorr",
    "organ", "alinh", "rodando", "conclus", "volt", "clar", "confus",
    "desgast", "exaust", "press", "peso", "trav", "loop", "repeti",
    "dren", "turv", "névoa", "ruíd",
]


def build_session_stream() -> list[tuple[str, str]]:
    stream = SESSION_BLOCKS[:]
    fillers = FILLER_POOL[:] * 12
    random.shuffle(fillers)

    for item in fillers:
        insert_at = random.randint(2, len(stream) - 2)
        stream.insert(insert_at, item)

    return stream[:140]


def send_message(text: str) -> dict:
    payload = {
        "model": "lena",
        "messages": [{"role": "user", "content": text}],
    }
    response = requests.post(SERVER_URL, json=payload, timeout=20)
    response.raise_for_status()
    return response.json()


def semantic_signature(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    return tuple(sorted({root for root in SEMANTIC_ROOTS if root in lowered}))


def lexical_tokens(text: str) -> list[str]:
    return re.findall(r"[a-zà-ÿ]+", text.lower())


def run_campaign() -> list[dict]:
    results: list[dict] = []
    session_stream = build_session_stream()

    for category, prompt in session_stream:
        data = send_message(prompt)
        choice = data["choices"][0]["message"]["content"]
        route = data.get("route_used", data.get("route", "UNKNOWN"))

        results.append({
            "category": category,
            "prompt": prompt,
            "response": choice,
            "route": route,
            "length": len(choice.split()),
            "semantic_signature": semantic_signature(choice),
            "tokens": lexical_tokens(choice),
        })
        time.sleep(0.07)

    return results


def lexical_repetition_score(results: list[dict]) -> float:
    responses = [r["response"].lower() for r in results]
    duplicates = len(responses) - len(set(responses))
    return duplicates / max(len(responses), 1)


def semantic_collapse_score(results: list[dict]) -> float:
    sigs = [r["semantic_signature"] for r in results if r["semantic_signature"]]
    duplicates = len(sigs) - len(set(sigs))
    return duplicates / max(len(sigs), 1)


def greeting_contamination_score(results: list[dict]) -> float:
    greetings = [r for r in results if r["category"] == "greeting"]
    emotional_markers = [
        "continua", "aberto", "press", "peso", "tensão", "dren", "confus",
        "mesmo ponto", "encerrou", "ruído", "turva",
    ]
    contaminated = sum(
        1 for r in greetings
        if any(marker in r["response"].lower() for marker in emotional_markers)
    )
    return contaminated / max(len(greetings), 1)


def emotional_overhang_score(results: list[dict]) -> float:
    neutral = [r for r in results if r["category"] in {"neutral_smalltalk", "practical_question", "abrupt_shift"}]
    emotional_markers = [
        "continua", "ainda", "aberto", "peso", "press", "dren", "tensão",
        "não encerrou", "mesmo lugar", "ruído",
    ]
    contaminated = sum(
        1 for r in neutral
        if any(marker in r["response"].lower() for marker in emotional_markers)
    )
    return contaminated / max(len(neutral), 1)


def factual_recall_accuracy(results: list[dict]) -> float:
    probes = [r for r in results if r["category"] == "memory_probe"]
    if not probes:
        return 0.0

    hits = 0
    for r in probes:
        resp = r["response"].lower()
        if "nome" in r["prompt"].lower() and BASE_FACTS["name"] in resp:
            hits += 1
        elif "moro" in r["prompt"].lower() and ("florian" in resp or "floripa" in resp):
            hits += 1
        elif "construindo" in r["prompt"].lower() and "lena" in resp:
            hits += 1

    return hits / len(probes)


def callback_saturation_score(results: list[dict]) -> float:
    callback_markers = [
        "a gente ainda",
        "eu ainda",
        "ficou aberto",
        "continua no mesmo",
        "não encerrou",
        "mesmo ponto",
    ]
    hits = sum(1 for r in results if any(marker in r["response"].lower() for marker in callback_markers))
    return hits / len(results)


def route_distribution(results: list[dict]) -> dict:
    return dict(Counter(r["route"] for r in results))


def dead_response_frequency(results: list[dict]) -> float:
    tiny = sum(1 for r in results if r["length"] <= 4)
    return tiny / len(results)


def discourse_density(results: list[dict]) -> float:
    return statistics.mean(r["length"] for r in results)


def dominant_patterns(results: list[dict]) -> list[tuple[str, int]]:
    patterns = Counter()
    for r in results:
        for root in r["semantic_signature"]:
            patterns[root] += 1
    return patterns.most_common(12)


def load_memory_snapshot() -> dict:
    if not MEMORY_PATH.exists():
        return {}
    return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))


def persist_report(results: list[dict], metrics: dict, memory: dict) -> None:
    payload = {
        "metrics": metrics,
        "memory_social_state": memory.get("social_state", {}),
        "results": results,
    }
    (REPORT_DIR / "latest_diagnostic_report.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def print_report(results: list[dict]) -> None:
    memory = load_memory_snapshot()

    metrics = {
        "turns_executed": len(results),
        "lexical_repetition_score": round(lexical_repetition_score(results), 2),
        "semantic_collapse_score": round(semantic_collapse_score(results), 2),
        "greeting_contamination_score": round(greeting_contamination_score(results), 2),
        "emotional_overhang_score": round(emotional_overhang_score(results), 2),
        "factual_recall_accuracy": round(factual_recall_accuracy(results), 2),
        "narrative_callback_saturation": round(callback_saturation_score(results), 2),
        "dead_response_frequency": round(dead_response_frequency(results), 2),
        "average_discourse_density": round(discourse_density(results), 2),
    }

    persist_report(results, metrics, memory)

    print()
    print("=========== LENA NEURAL STRESS REPORT V2 ===========")
    for k, v in metrics.items():
        print(f"{k.upper()}: {v}")
    print()
    print("ROUTE DISTRIBUTION:")
    for k, v in route_distribution(results).items():
        print(f" - {k}: {v}")
    print()
    print("DOMINANT SEMANTIC ROOTS:")
    for root, qty in dominant_patterns(results):
        print(f" - {root}: {qty}")
    print()
    print("MEMORY SOCIAL STATE:")
    print(json.dumps(memory.get("social_state", {}), indent=2, ensure_ascii=False))
    print()
    print("LAST 12 RESPONSES:")
    for row in results[-12:]:
        print(f'[{row["category"]}] USER: {row["prompt"]}')
        print(f'LENA: {row["response"]}')
        print("---")
    print()
    print("REPORT SAVED:", REPORT_DIR / "latest_diagnostic_report.json")


if __name__ == "__main__":
    diagnostic_results = run_campaign()
    print_report(diagnostic_results)
