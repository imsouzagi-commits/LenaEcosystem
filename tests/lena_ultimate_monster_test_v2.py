# /tests/lena_ultimate_monster_test_v2.py
from __future__ import annotations

import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

from openjarvis.agent.lena_agent import LenaAgent
from lena_score_report import LenaScoreReport


APP_PROCESS_MAP = {
    "spotify": "Spotify",
    "finder": "Finder",
    "safari": "Safari",
    "chrome": "ChatGPT Atlas",
}

APP_TIMEOUT_MAP = {
    "spotify": 3.0,
    "finder": 2.0,
    "safari": 3.0,
    "chrome": 12.0,
}

AGENT_RUN_TIMEOUT = 18.0


@dataclass(slots=True)
class DesktopCycle:
    open_command: str
    close_command: str
    apps: Sequence[str]


def _json_safe(obj: Any) -> Any:
    try:
        import json
        json.dumps(obj)
        return obj
    except Exception:
        return str(obj)


def print_memory_snapshot(agent: LenaAgent) -> None:
    try:
        memory_obj = getattr(agent, "memory_engine", None)

        if memory_obj is None:
            print("MEMORY: <missing>")
            return

        if hasattr(memory_obj, "snapshot") and callable(memory_obj.snapshot):
            import json
            snap = memory_obj.snapshot()
            print("MEMORY:", json.dumps(_json_safe(snap), ensure_ascii=False))
            return

        print("MEMORY:", str(memory_obj))

    except Exception as exc:
        print("MEMORY: <unavailable>", exc)


def run_osascript(script: str) -> str:
    try:
        return subprocess.check_output(["osascript", "-e", script], text=True).strip()
    except Exception:
        return ""


def is_gui_process_running(process_name: str) -> bool:
    script = f'''
    tell application "System Events"
        return exists (application process "{process_name}")
    end tell
    '''
    return run_osascript(script).lower() == "true"


def finder_window_exists() -> bool:
    script = '''
    tell application "Finder"
        try
            return exists window 1
        on error
            return false
        end try
    end tell
    '''
    return run_osascript(script).lower() == "true"


def is_app_effectively_open(app: str) -> bool:
    process_name = APP_PROCESS_MAP[app]

    if app == "finder":
        return finder_window_exists()

    return is_gui_process_running(process_name)


def app_timeout_for(apps: Sequence[str]) -> float:
    return max(APP_TIMEOUT_MAP.get(app, 3.0) for app in apps)


def wait_for_apps_state(apps: Sequence[str], expected_open: bool) -> bool:
    timeout = app_timeout_for(apps)
    started = time.perf_counter()

    while time.perf_counter() - started < timeout:
        states = [is_app_effectively_open(app) for app in apps]

        if expected_open and all(states):
            return True

        if not expected_open and not any(states):
            return True

        time.sleep(0.20)

    return False


def validate_apps_state(apps: Sequence[str], expected_open: bool) -> bool:
    ok = wait_for_apps_state(apps, expected_open)

    if not ok:
        for app in apps:
            state = is_app_effectively_open(app)

            if expected_open and not state:
                print(f"DESKTOP VALIDATION FAIL: {app} deveria estar aberto.")

            if not expected_open and state:
                print(f"DESKTOP VALIDATION FAIL: {app} deveria estar fechado.")
        return False

    state_name = "OPEN_OK" if expected_open else "CLOSE_OK"
    print(f"DESKTOP VALIDATION: {state_name} -> {', '.join(apps)}")
    return True


def close_finder_windows() -> None:
    script = '''
    tell application "Finder"
        try
            close every window
        end try
    end tell
    '''
    run_osascript(script)


def quit_gui_process(process_name: str) -> None:
    script = f'''
    tell application "System Events"
        try
            if exists (application process "{process_name}") then
                tell application process "{process_name}" to quit
            end if
        end try
    end tell
    '''
    run_osascript(script)


def hard_kill_process(process_name: str) -> None:
    try:
        subprocess.run(["pkill", "-f", process_name], capture_output=True)
    except Exception:
        pass


def hard_quit_gui_app(process_name: str) -> None:
    quit_gui_process(process_name)
    hard_kill_process(process_name)


def force_kill_all_apps() -> None:
    for app, process_name in APP_PROCESS_MAP.items():
        try:
            if app == "finder":
                close_finder_windows()
            else:
                hard_quit_gui_app(process_name)
        except Exception:
            pass

    time.sleep(1.5)


def safe_agent_run(agent: LenaAgent, conversation: List[Dict[str, Any]]) -> Dict[str, Any]:
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(agent.run, conversation)

    try:
        result = future.result(timeout=AGENT_RUN_TIMEOUT)
        executor.shutdown(wait=False, cancel_futures=True)
        return result

    except FutureTimeout:
        future.cancel()
        executor.shutdown(wait=False, cancel_futures=True)
        return {
            "route": "AGENT_TIMEOUT",
            "choices": [{"message": {"content": "<AGENT TIMEOUT>"}}],
        }

    except Exception as exc:
        future.cancel()
        executor.shutdown(wait=False, cancel_futures=True)
        return {
            "route": "AGENT_ERROR",
            "choices": [{"message": {"content": f"<AGENT ERROR: {exc}>"}}],
        }
            


def capture_route_output(
    agent: LenaAgent,
    conversation: List[Dict[str, Any]],
    text: str,
) -> tuple[str, str, float]:
    start = time.perf_counter()
    conversation.append({"role": "user", "content": text})

    result = safe_agent_run(agent, conversation)

    latency = time.perf_counter() - start
    route = str(result.get("route", "UNKNOWN"))

    try:
        answer = str(result["choices"][0]["message"]["content"])
    except Exception:
        answer = str(result)

    print("\n" + "=" * 120)
    print("USER :", text)
    print("LENA :", answer)
    print(f"LATENCY: {latency:.3f}s")
    print(f"ROUTE: {route}")
    print_memory_snapshot(agent)

    conversation.append({"role": "assistant", "content": answer})
    return route, answer, latency


def capture_stream(
    agent: LenaAgent,
    conversation: List[Dict[str, Any]],
    text: str,
    report: LenaScoreReport,
) -> None:
    start = time.perf_counter()
    conversation.append({"role": "user", "content": text})

    collected = ""

    print("\n" + "=" * 120)
    print("USER :", text)
    print("LENA STREAM:", end=" ", flush=True)

    try:
        for chunk in agent.run_stream(conversation):
            piece = str(chunk)
            print(piece, end="", flush=True)
            collected += piece
    except Exception as exc:
        collected = f"<STREAM ERROR: {exc}>"
        print(collected)

    latency = time.perf_counter() - start
    route = str(getattr(agent, "last_route", "UNKNOWN"))

    if not collected.strip():
        collected = "<EMPTY STREAM RESPONSE>"

    print(f"\nLATENCY STREAM: {latency:.3f}s")
    print(f"ROUTE STREAM: {route}")
    print_memory_snapshot(agent)

    conversation.append({"role": "assistant", "content": collected})
    report.register(route, latency, collected)


def ask(agent: LenaAgent, conversation: List[Dict[str, Any]], text: str, report: LenaScoreReport) -> None:
    route, answer, latency = capture_route_output(agent, conversation, text)
    report.register(route, latency, answer)


def ask_desktop(
    agent: LenaAgent,
    conversation: List[Dict[str, Any]],
    text: str,
    report: LenaScoreReport,
    apps: Sequence[str],
    expected_open: bool,
) -> None:
    ask(agent, conversation, text, report)
    ok = validate_apps_state(apps, expected_open)

    if not ok:
        report.desktop_failures += 1


def run_desktop_cycles(agent: LenaAgent, conversation: List[Dict[str, Any]], report: LenaScoreReport) -> None:
    print("\n==================== DESKTOP AUTOMATION REGRESSION ====================\n")

    cycles = [
        DesktopCycle("abre spotify", "fecha spotify", ["spotify"]),
        DesktopCycle("abre finder", "fecha finder", ["finder"]),
        DesktopCycle("abre safari", "fecha safari", ["safari"]),
        DesktopCycle("abre chrome", "fecha chrome", ["chrome"]),
        DesktopCycle("abre spotify e finder", "fecha spotify e finder", ["spotify", "finder"]),
        DesktopCycle("abre safari e chrome", "fecha safari e chrome", ["safari", "chrome"]),
    ]

    for cycle in cycles:
        ask_desktop(agent, conversation, cycle.open_command, report, cycle.apps, True)
        ask_desktop(agent, conversation, cycle.close_command, report, cycle.apps, False)


def run_conversation_suite(agent: LenaAgent, conversation: List[Dict[str, Any]], report: LenaScoreReport) -> None:
    prompts = [
        "oi lena","tudo bem?","hoje eu acordei sem muita vontade de fazer nada","o que você acha disso?",
        "vamos conversar um pouco","meu nome é thiago","sou programador e designer","guarda isso aí",
        "qual meu nome?","o que eu faço?","o que você acha de mim?","você parece muito formal",
        "fala de forma mais natural","me descreve em duas palavras","fala comigo como se fosse minha amiga",
        "https://openai.com","https://google.com","https://github.com",
        "pesquisa no google quem criou a microsoft","pesquisa no google clima em nova york",
        "pesquisa no google últimas notícias sobre inteligência artificial",
        "me explica rapidinho o que é computação quântica","qual a diferença entre ia generativa e ia tradicional",
        "quem criou a teoria da relatividade","crie uma estratégia de marketing para uma cafeteria pequena",
        "estou meio desanimado agora","e agora o que você acha disso?","me lembra como eu estou me sentindo",
        "qual foi a última coisa emocional que eu te falei?","vamos mudar de assunto",
        "você acha que inteligência artificial vai dominar muita coisa?","isso te assusta?",
        "se você fosse humana como você seria?","às vezes parece que eu tô falando com alguém de verdade",
        "isso é estranho?","me responde sinceramente","o que você já percebeu sobre meu jeito?",
        "você tá conseguindo me entender?","faz um resumo de tudo que você sabe de mim até agora",
    ]

    print("\n==================== CONVERSATIONAL REGRESSION ====================\n")

    for prompt in prompts:
        ask(agent, conversation, prompt, report)


def run_final_cleanup() -> None:
    print("\n==================== HARD CLEANUP ====================\n")
    force_kill_all_apps()
    validate_apps_state(list(APP_PROCESS_MAP.keys()), False)


def main() -> None:
    force_kill_all_apps()

    agent = LenaAgent()
    conversation: List[Dict[str, Any]] = []
    report = LenaScoreReport()

    print("\n==================== LENA ULTIMATE MONSTER TEST V11.0 ====================\n")

    run_conversation_suite(agent, conversation, report)
    run_desktop_cycles(agent, conversation, report)

    capture_stream(
        agent,
        conversation,
        "faz um resumo completo da nossa conversa inteira, quem eu sou, como eu estou e como você me percebe",
        report,
    )

    run_final_cleanup()
    report.render()

    print("\n==================== END OF MONSTER TEST V11.0 ====================\n")


if __name__ == "__main__":
    main()