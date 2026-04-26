from __future__ import annotations

import subprocess
import difflib
import logging
from pathlib import Path
from typing import Dict


class ActionCenter:
    def __init__(self):
        self.logger = logging.getLogger("ActionCenter")
        self.installed_apps = self._scan_apps()

    def _scan_apps(self) -> Dict[str, str]:
        app_map: Dict[str, str] = {
            "spotify": "Spotify",
            "safari": "Safari",
            "finder": "Finder",
            "whatsapp": "WhatsApp",
            "notes": "Notes",
            "chatgpt": "ChatGPT",
            "ableton": "Ableton Live 12 Suite",
        }

        applications = Path("/Applications")
        if applications.exists():
            for item in applications.iterdir():
                if item.is_dir() and item.name.endswith(".app"):
                    clean = item.name.replace(".app", "").lower().strip()
                    app_map[clean] = item.name.replace(".app", "")

        return app_map

    def resolve_app(self, name: str) -> str | None:
        if not name:
            return None

        exact = self.installed_apps.get(name.lower().strip())
        if exact:
            return exact

        matches = difflib.get_close_matches(name.lower().strip(), self.installed_apps.keys(), n=1, cutoff=0.68)
        if matches:
            return self.installed_apps[matches[0]]

        return None

    def open_app(self, name: str) -> str:
        app = self.resolve_app(name)
        if not app:
            return f"App não encontrado: {name}"

        subprocess.Popen(["open", "-a", app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Abrindo {app}"

    def close_app(self, name: str) -> str:
        app = self.resolve_app(name)
        if not app:
            return f"App não encontrado: {name}"

        subprocess.Popen(
            ["osascript", "-e", f'tell application "{app}" to quit'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return f"Fechando {app}"

    def wifi_on(self) -> str:
        subprocess.Popen(["networksetup", "-setairportpower", "en0", "on"])
        return "Ligando Wi-Fi"

    def wifi_off(self) -> str:
        subprocess.Popen(["networksetup", "-setairportpower", "en0", "off"])
        return "Desligando Wi-Fi"

    def volume_up(self) -> str:
        subprocess.Popen(["osascript", "-e", "set volume output volume ((output volume of (get volume settings)) + 10)"])
        return "Aumentando volume"

    def volume_down(self) -> str:
        subprocess.Popen(["osascript", "-e", "set volume output volume ((output volume of (get volume settings)) - 10)"])
        return "Diminuindo volume"

    def brightness_up(self) -> str:
        subprocess.Popen(["brightness", "0.8"])
        return "Aumentando brilho"

    def brightness_down(self) -> str:
        subprocess.Popen(["brightness", "0.3"])
        return "Diminuindo brilho"