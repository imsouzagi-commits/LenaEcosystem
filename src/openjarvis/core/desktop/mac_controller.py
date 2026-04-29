# src/openjarvis/core/desktop/mac_controller.py

from __future__ import annotations

import subprocess
import time
from typing import Iterable


class MacDesktopController:
    APP_ALIASES = {
        "spotify": "Spotify",
        "finder": "Finder",
        "safari": "Safari",
        "chrome": "Google Chrome",
        "google chrome": "Google Chrome",
        "firefox": "Firefox",
        "terminal": "Terminal",
        "notes": "Notes",
        "notas": "Notes",
        "mail": "Mail",
        "mensagens": "Messages",
        "messages": "Messages",
        "discord": "Discord",
        "slack": "Slack",
        "github desktop": "GitHub Desktop",
        "vscode": "Visual Studio Code",
        "visual studio code": "Visual Studio Code",
    }

    @classmethod
    def normalize_app_name(cls, raw_name: str) -> str:
        key = raw_name.strip().lower()
        return cls.APP_ALIASES.get(key, raw_name.strip())

    @staticmethod
    def _run_osascript(script: str) -> None:
        subprocess.run(["osascript", "-e", script], capture_output=True)

    @classmethod
    def close_app(cls, app_name: str) -> None:
        app = cls.normalize_app_name(app_name)
        cls._run_osascript(f'tell application "{app}" to quit')

    @classmethod
    def force_close_app(cls, app_name: str) -> None:
        app = cls.normalize_app_name(app_name)
        subprocess.run(["pkill", "-x", app], capture_output=True)

    @classmethod
    def open_app(cls, app_name: str) -> None:
        app = cls.normalize_app_name(app_name)

        cls.close_app(app)
        time.sleep(0.4)
        cls.force_close_app(app)
        time.sleep(0.3)

        subprocess.run(["open", "-a", app], capture_output=True)

    @classmethod
    def open_multiple_apps(cls, app_names: Iterable[str]) -> None:
        for app in app_names:
            cls.open_app(app)

    @classmethod
    def close_multiple_apps(cls, app_names: Iterable[str]) -> None:
        for app in app_names:
            cls.close_app(app)