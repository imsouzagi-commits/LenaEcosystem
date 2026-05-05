from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from openjarvis.agent.lena_agent import LenaAgent


OUTPUT_DIR = Path.home() / "LenaWorkspace" / "Delivery" / "test_runs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def is_app_running(app_name: str) -> bool:
    script = f'''
    tell application "System Events"
        return (name of every process) contains "{app_name}"
    end tell
    '''
    try:
        proc = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=3)
        return "true" in proc.stdout.lower()
    except Exception:
        return False


def safe_agent_run(agent: LenaAgent, conversation: List[Dict[str, Any]]) -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        result = agent.run(conversation)
        result["_hard_latency"] = round(time.perf_counter() - started, 3)
        return result
    except Exception as exc:
        return {
            "choices": [{"message": {"content": f"EXCEPTION: {exc}"}}],
            "route": "EXCEPTION",
            "_hard_latency": round(time.perf_counter() - started, 3),
        }


def log_step(transcript: List[dict[str, Any]], payload: dict[str, Any]) -> None:
    transcript.append(payload)
    print("\n" + "=" * 120)
    for k, v in payload.items():
        print(f"{k}: {v}")


def ask(
    agent: LenaAgent,
    conversation: List[Dict[str, Any]],
    transcript: List[dict[str, Any]],
    text: str,
    expected_route: Optional[str] = None,
) -> Dict[str, Any]:
    conversation.append({"role": "user", "content": text})

    result = safe_agent_run(agent, conversation)

    answer = result["choices"][0]["message"]["content"]
    route = result.get("route", "UNKNOWN")
    latency = result.get("_hard_latency", 0.0)

    payload = {
        "user": text,
        "answer": answer,
        "route": route,
        "latency": latency,
        "expected_route": expected_route,
        "route_ok": expected_route is None or expected_route == route,
    }

    log_step(transcript, payload)
    conversation.append({"role": "assistant", "content": answer})
    return result


def save_transcript(transcript: List[dict[str, Any]]) -> Path:
    filename = OUTPUT_DIR / f"lena_validation_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    filename.write_text(json.dumps(transcript, indent=2, ensure_ascii=False))
    return filename


def main() -> None:
    agent = LenaAgent()
    conversation: List[Dict[str, Any]] = []
    transcript: List[dict[str, Any]] = []

    time.sleep(1)

    print("\n==================== LENA MASTER VALIDATION V13 ====================\n")

    ask(agent, conversation, transcript, "oi lena")
    ask(agent, conversation, transcript, "meu nome é thiago")
    ask(agent, conversation, transcript, "sou programador e designer")
    ask(agent, conversation, transcript, "qual meu nome?", "MEMORY_SUMMARY")
    ask(agent, conversation, transcript, "o que eu faço?", "MEMORY_SUMMARY")

    ask(agent, conversation, transcript, "abre safari", "DESKTOP")
    safari_opened = is_app_running("Safari")
    log_step(transcript, {"os_check_safari_opened": safari_opened})

    ask(agent, conversation, transcript, "fecha safari", "DESKTOP")
    safari_closed = not is_app_running("Safari")
    log_step(transcript, {"os_check_safari_closed": safari_closed})

    ask(agent, conversation, transcript, "abre atlas", "DESKTOP")
    atlas_opened = is_app_running("ChatGPT Atlas")
    log_step(transcript, {"os_check_atlas_opened": atlas_opened})

    ask(agent, conversation, transcript, "google carros elétricos 2026", "WEB_SEARCH")
    ask(agent, conversation, transcript, "/lena page", "MEMORY_SUMMARY")
    ask(agent, conversation, transcript, "/lena status", "MEMORY_SUMMARY")

    ask(agent, conversation, transcript, "estou meio cansado hoje")
    ask(agent, conversation, transcript, "me lembra como eu estou me sentindo", "MEMORY_SUMMARY")
    ask(agent, conversation, transcript, "o que você acha de mim?", "MEMORY_SUMMARY")

    ask(agent, conversation, transcript, "fecha chatgpt", "DESKTOP")
    ask(agent, conversation, transcript, "fecha atlas", "DESKTOP")

    output = save_transcript(transcript)

    route_pass = sum(1 for x in transcript if x.get("route_ok") is True)
    route_total = sum(1 for x in transcript if "route_ok" in x)
    avg_latency = round(
        sum(x.get("latency", 0.0) for x in transcript if "latency" in x) / max(1, len([x for x in transcript if "latency" in x])),
        3,
    )

    print("\n==================== FINAL SCORE ====================")
    print("ROUTE ASSERTIONS:", f"{route_pass}/{route_total}")
    print("AVG LATENCY:", avg_latency)
    print("TRANSCRIPT:", output)
    print("====================================================\n")


if __name__ == "__main__":
    main()
