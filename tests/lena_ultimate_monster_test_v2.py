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
    "chrome": "Google Chrome",
}

APP_TIMEOUT_MAP = {
    "spotify": 3.0,
    "finder": 2.0,
    "safari": 3.0,
    "chrome": 4.0,
}

AGENT_RUN_TIMEOUT = 18.0


@dataclass(slots=True)
class DesktopCycle:
    open_command: str
    close_command: str
    apps: Sequence[str]


def print_memory_snapshot(agent: LenaAgent) -> None:
    try:
        print("MEMORY:", agent.memory_engine.memory_health_report())
    except Exception as exc:
        print("MEMORY SNAPSHOT FAIL:", exc)


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
    if app == "finder":
        return finder_window_exists()
    return is_gui_process_running(APP_PROCESS_MAP[app])


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

    print("DESKTOP VALIDATION:", "OPEN_OK" if expected_open else "CLOSE_OK", "->", ", ".join(apps))
    return True


def close_finder_windows() -> None:
    run_osascript('tell application "Finder" to close every window')


def hard_quit_gui_app(process_name: str) -> None:
    run_osascript(f'''
    tell application "System Events"
        try
            if exists (application process "{process_name}") then
                tell application process "{process_name}" to quit
            end if
        end try
    end tell
    ''')
    try:
        subprocess.run(["pkill", "-f", process_name], capture_output=True)
    except Exception:
        pass


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
        return {"route": "AGENT_TIMEOUT", "choices": [{"message": {"content": "<AGENT TIMEOUT>"}}]}
    except Exception as exc:
        future.cancel()
        executor.shutdown(wait=False, cancel_futures=True)
        return {"route": "AGENT_ERROR", "choices": [{"message": {"content": f"<AGENT ERROR: {exc}>"}}]}


def capture(agent: LenaAgent, conversation: List[Dict[str, Any]], text: str) -> tuple[str, str, float]:
    started = time.perf_counter()
    conversation.append({"role": "user", "content": text})

    result = safe_agent_run(agent, conversation)

    latency = time.perf_counter() - started
    route = str(result.get("route", "UNKNOWN"))
    answer = str(result["choices"][0]["message"]["content"])

    print("\n" + "=" * 120)
    print("USER :", text)
    print("LENA :", answer)
    print(f"LATENCY: {latency:.3f}s")
    print("ROUTE :", route)
    print_memory_snapshot(agent)

    conversation.append({"role": "assistant", "content": answer})
    return route, answer, latency


def ask(agent: LenaAgent, conversation: List[Dict[str, Any]], text: str, report: LenaScoreReport) -> None:
    route, answer, latency = capture(agent, conversation, text)
    report.register(route, latency, answer)


def ask_desktop(agent: LenaAgent, conversation: List[Dict[str, Any]], text: str, report: LenaScoreReport, apps: Sequence[str], expected_open: bool) -> None:
    ask(agent, conversation, text, report)
    if not validate_apps_state(apps, expected_open):
        report.desktop_failures += 1


def run_conversation_suite(agent: LenaAgent, conversation: List[Dict[str, Any]], report: LenaScoreReport) -> None:
    prompts = [
        "oi lena",
        "hoje acordei meio sem vontade",
        "o que você acha disso?",
        "meu nome é thiago",
        "sou programador e designer",
        "qual meu nome?",
        "o que eu faço?",
        "quem criou o spotify",
        "e quem era ele?",
        "quem fundou a tesla",
        "procura arquivo cognitive orchestrator",
        "procura projeto memory facade",
        "me explica rapidinho o que é computação quântica",
        "você acha que ia vai dominar muita coisa?",
        "to cansado hoje",
        "me descreve em duas palavras",
        "faz um resumo de tudo que você sabe de mim",
    ]

    print("\n==================== CONVERSATIONAL + SEARCH SUITE ====================\n")

    for prompt in prompts:
        ask(agent, conversation, prompt, report)


def run_desktop_cycles(agent: LenaAgent, conversation: List[Dict[str, Any]], report: LenaScoreReport) -> None:
    print("\n==================== DESKTOP AUTOMATION SUITE ====================\n")

    cycles = [
        DesktopCycle("abre spotify", "fecha spotify", ["spotify"]),
        DesktopCycle("abre finder", "fecha finder", ["finder"]),
        DesktopCycle("abre safari", "fecha safari", ["safari"]),
        DesktopCycle("abre chrome", "fecha chrome", ["chrome"]),
    ]

    for cycle in cycles:
        ask_desktop(agent, conversation, cycle.open_command, report, cycle.apps, True)
        ask_desktop(agent, conversation, cycle.close_command, report, cycle.apps, False)


def main() -> None:
    force_kill_all_apps()

    agent = LenaAgent()
    conversation: List[Dict[str, Any]] = []
    report = LenaScoreReport()

    print("\n==================== LENA ULTIMATE MONSTER TEST V12 ====================\n")

    run_conversation_suite(agent, conversation, report)
    run_desktop_cycles(agent, conversation, report)

    report.render()
    force_kill_all_apps()

    print("\n==================== END OF MONSTER TEST V12 ====================\n")


if __name__ == "__main__":
    main()
