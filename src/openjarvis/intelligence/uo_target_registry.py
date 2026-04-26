from __future__ import annotations

from typing import Dict


class UOTargetRegistry:
    def __init__(self, installed_apps: Dict[str, str]):
        self.installed_apps = installed_apps

        self.system_targets = {
            "wifi": "wifi",
            "wi fi": "wifi",
            "bluetooth": "bluetooth",
            "volume": "volume",
            "som": "volume",
            "audio": "volume",
            "brilho": "brilho",
            "tela": "brilho",
        }

    def all_targets(self) -> Dict[str, str]:
        merged = {}
        merged.update(self.system_targets)
        merged.update(self.installed_apps)
        return merged