from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from typing import List, Sequence

from openjarvis.agent.lena_agent import LenaAgent


APP_PROCESS_MAP = {
    "spotify": "Spotify",
    "finder": "Finder",
    "safari": "Safari",
    "chrome": "Google Chrome",
    "notes": "Notes",
    "calculator": "Calculator",
}

APP_TIMEOUT_MAP = {
    "spotify": 2.5,
    "finder": 1.2,
    "safari": 2.0,
    "chrome": 3.0,
    "notes": 1.5,
    "calculator": 1.2,
}


@dataclass(slots=True)
class DesktopCase:
    app: str
    open_cmd: str
    close_cmd: str


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


def is_open(app: str) -> bool:
    if app == "finder":
        return finder_window_exists()
    return is_gui_process_running(APP_PROCESS_MAP[app])


def wait_state(app: str, expected_open: bool) -> bool:
    timeout = APP_TIMEOUT_MAP.get(app, 2.0)
    started = time.perf_counter()

    while time.perf_counter() - started < timeout:
        state = is_open(app)

        if expected_open and state:
            return True

        if not expected_open and not state:
            return True

        time.sleep(0.10)

    return False


def hard_cleanup() -> None:
    run_osascript('tell application "Finder" to close every window')

    for proc in APP_PROCESS_MAP.values():
        try:
            subprocess.run(["pkill", "-f", proc], capture_output=True)
        except Exception:
            pass

    time.sleep(1.0)


def ask(agent: LenaAgent, text: str) -> tuple[str, float]:
    started = time.perf_counter()
    result = agent.run([{"role": "user", "content": text}])
    latency = time.perf_counter() - started
    answer = str(result["choices"][0]["message"]["content"])
    return answer, latency


def run_case(agent: LenaAgent, case: DesktopCase) -> None:
    print("\n" + "=" * 120)
    print("APP:", case.app.upper())

    answer, latency = ask(agent, case.open_cmd)
    opened = wait_state(case.app, True)

    print("OPEN CMD :", case.open_cmd)
    print("OPEN RES :", answer)
    print("OPEN LAT :", f"{latency:.3f}s")
    print("OPEN OK? :", opened)

    answer, latency = ask(agent, case.close_cmd)
    closed = wait_state(case.app, False)

    print("CLOSE CMD:", case.close_cmd)
    print("CLOSE RES:", answer)
    print("CLOSE LAT:", f"{latency:.3f}s")
    print("CLOSE OK?:", closed)


def main() -> None:
    hard_cleanup()

    agent = LenaAgent()

    cases: List[DesktopCase] = [
        DesktopCase("safari", "abre safari", "fecha safari"),
        DesktopCase("spotify", "abre spotify", "fecha spotify"),
        DesktopCase("finder", "abre finder", "fecha finder"),
        DesktopCase("chrome", "abre chrome", "fecha chrome"),
        DesktopCase("notes", "abre notes", "fecha notes"),
        DesktopCase("calculator", "abre calculator", "fecha calculator"),
    ]

    print("\n" + "=" * 120)
    print("LENA DESKTOP STRESS TEST")
    print("=" * 120)

    for _ in range(2):
        for case in cases:
            run_case(agent, case)

    hard_cleanup()
    print("\n" + "=" * 120)
    print("END DESKTOP STRESS TEST")
    print("=" * 120)


if __name__ == "__main__":
    main()
