from __future__ import annotations

import re
import subprocess
from typing import List, Tuple

from openjarvis.lena.action_guard import LenaActionGuard
from openjarvis.lena.app_registry import LenaAppRegistry
from openjarvis.lena.runtime_guard import LenaRuntimeGuard
from openjarvis.lena.task_context import LenaTaskContext


class LenaDesktopController:
    def __init__(self, kernel) -> None:
        self.kernel = kernel

    def _normalize_app_name(self, raw: str) -> str:
        cleaned = raw.lower().strip().replace(".", "")
        cleaned = " ".join(cleaned.split())

        if cleaned in {"ele", "ela", "isso", "esse app"}:
            resolved = LenaTaskContext.consume_last_app()
            if resolved:
                return resolved

        return LenaAppRegistry.APP_NAME_MAP.get(cleaned, raw.strip().title())

    def _split_apps(self, payload: str) -> List[str]:
        payload = payload.replace(" e depois ", ",")
        payload = payload.replace(" depois ", ",")
        payload = payload.replace(" e ", ",")
        return [x.strip() for x in payload.split(",") if x.strip()]

    def _extract_commands(self, user_text: str) -> List[Tuple[str, str]]:
        lowered = user_text.lower().strip()
        lowered = lowered.replace("abrir ", "abre ")
        lowered = lowered.replace("fechar ", "fecha ")
        lowered = lowered.replace("encerra ", "fecha ")

        commands: List[Tuple[str, str]] = []
        parts = re.split(r"\b(?=abre |fecha )", lowered)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            if part.startswith("abre "):
                payload = part[5:].strip(" ,.")
                for app in self._split_apps(payload):
                    commands.append(("open", self._normalize_app_name(app)))

            elif part.startswith("fecha "):
                payload = part[6:].strip(" ,.")
                for app in self._split_apps(payload):
                    commands.append(("close", self._normalize_app_name(app)))

        return commands

    @staticmethod
    def _run_applescript(script: str) -> bool:
        try:
            subprocess.run(
                ["osascript", "-e", script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
                timeout=8,
            )
            return True
        except Exception:
            return False

    def _hard_open_app(self, app_name: str) -> bool:
        allowed, _ = LenaActionGuard.allow("open_app", app_name)
        if not allowed:
            return False

        app_path = LenaAppRegistry.APP_PATH_MAP.get(app_name)

        try:
            if app_path:
                subprocess.Popen(["open", app_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(["open", "-a", app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            subprocess.Popen(
                ["osascript", "-e", f'tell application "{app_name}" to activate'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except Exception:
            return False

    def _hard_close_app(self, app_name: str) -> bool:
        allowed, _ = LenaActionGuard.allow("close_app", app_name)
        if not allowed:
            return False

        if not LenaRuntimeGuard.can_close(app_name):
            return False

        try:
            subprocess.Popen(
                ["osascript", "-e", f'tell application "{app_name}" to quit'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            subprocess.Popen(
                ["pkill", "-f", app_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            if app_name == "Finder":
                subprocess.Popen(
                    ["osascript", "-e", 'tell application "Finder" to close every window'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            return True
        except Exception:
            return False

    def execute(self, user_text: str) -> str:
        outputs: List[str] = []

        for action, app_name in self._extract_commands(user_text):
            try:
                if action == "open":
                    ok = self._hard_open_app(app_name)
                    if ok:
                        LenaTaskContext.remember_app(app_name)
                    outputs.append(f"abri {app_name}" if ok else f"não consegui abrir {app_name}")
                else:
                    ok = self._hard_close_app(app_name)
                    if ok:
                        LenaTaskContext.forget_app(app_name)
                    outputs.append(f"fechei {app_name}" if ok else f"não consegui fechar {app_name}")
            except Exception:
                outputs.append(f"não consegui mexer no {app_name}")

        return ". ".join(outputs) + "."
