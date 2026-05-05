from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

from openjarvis.agent.lena_agent import LenaAgent
from lena_score_report import LenaScoreReport


APP_PROCESS_MAP = {
    "spotify": "Spotify",
    "finder": "Finder",
    "safari": "Safari",
}

APP_TIMEOUT_MAP = {
    "spotify": 2.5,
    "finder": 1.5,
    "safari": 2.5,
}


@dataclass(slots=True)
class DesktopCycle:
    open_command: str
    close_command: str
    apps: Sequence[str]


def run_osascript(script: str) -> str:
    try:
        return subprocess.check_output(["osascript", "-e", script], text=True).strip()
    except Exception:
        return ""


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


def is_gui_process_running(process_name: str) -> bool:
    script = f'''
    tell application "System Events"
        return exists (application process "{process_name}")
    end tell
    '''
    return run_osascript(script).lower() == "true"


def is_app_open(app: str) -> bool:
    if app == "finder":
        return finder_window_exists()
    return is_gui_process_running(APP_PROCESS_MAP[app])


def wait_for_state(apps: Sequence[str], expected_open: bool) -> bool:
    timeout = max(APP_TIMEOUT_MAP.get(app, 2.0) for app in apps)
    started = time.perf_counter()

    while time.perf_counter() - started < timeout:
        states = [is_app_open(app) for app in apps]

        if expected_open and all(states):
            return True

        if not expected_open and not any(states):
            return True

        time.sleep(0.15)

    return False


def force_clean_apps() -> None:
    run_osascript('tell application "Finder" to close every window')

    for process in APP_PROCESS_MAP.values():
        try:
            subprocess.run(["pkill", "-f", process], capture_output=True)
        except Exception:
            pass

    time.sleep(1.0)


def ask(agent: LenaAgent, conversation: List[Dict[str, Any]], text: str, report: LenaScoreReport) -> str:
    started = time.perf_counter()

    conversation.append({"role": "user", "content": text})
    result = agent.run(conversation)

    latency = time.perf_counter() - started
    route = str(result.get("route", "UNKNOWN"))
    answer = str(result["choices"][0]["message"]["content"])

    print("\\n" + "=" * 120)
    print("USER   :", text)
    print("ROUTE  :", route)
    print("LATENCY:", f"{latency:.3f}s")
    print("LENA   :", answer)

    conversation.append({"role": "assistant", "content": answer})
    report.register(route, latency, answer)

    return answer


def ask_desktop(
    agent: LenaAgent,
    conversation: List[Dict[str, Any]],
    text: str,
    report: LenaScoreReport,
    apps: Sequence[str],
    expected_open: bool,
) -> None:
    ask(agent, conversation, text, report)

    ok = wait_for_state(apps, expected_open)

    if ok:
        print("DESKTOP : OK")
    else:
        print("DESKTOP : FAIL")
        report.register_desktop_failure()


def run_suite(agent: LenaAgent, conversation: List[Dict[str, Any]], report: LenaScoreReport) -> None:
    prompts = [
        "oi lena",
        "meu nome é thiago",
        "qual meu nome?",
        "quem criou o spotify",
        "e quem era ele?",
        "procura arquivo cognitive orchestrator",
        "to cansado hoje",
        "faz um resumo de tudo que você sabe de mim",
    ]

    for prompt in prompts:
        ask(agent, conversation, prompt, report)

    desktop_cycles = [
        DesktopCycle("abre safari", "fecha safari", ["safari"]),
        DesktopCycle("abre spotify", "fecha spotify", ["spotify"]),
        DesktopCycle("abre finder", "fecha finder", ["finder"]),
    ]

    for cycle in desktop_cycles:
        ask_desktop(agent, conversation, cycle.open_command, report, cycle.apps, True)
        ask_desktop(agent, conversation, cycle.close_command, report, cycle.apps, False)


def main() -> None:
    force_clean_apps()

    agent = LenaAgent()
    conversation: List[Dict[str, Any]] = []
    report = LenaScoreReport()

    print("\\n" + "=" * 120)
    print("LENA ULTIMATE MONSTER TEST V3")
    print("=" * 120)

    run_suite(agent, conversation, report)

    print("\\n")
    report.render()
    force_clean_apps()


if __name__ == "__main__":
    main()
