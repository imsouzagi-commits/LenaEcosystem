from __future__ import annotations

import webbrowser

from openjarvis.core.desktop.mac_controller import MacDesktopController
from openjarvis.lena.command_center import LenaCommandCenter


class LenaActionCenter:
    @classmethod
    def try_execute(cls, user_text: str) -> str | None:
        parsed = LenaCommandCenter.parse(user_text)

        if not parsed:
            return None

        if parsed.action == "open":
            MacDesktopController.open_multiple_apps(parsed.targets)
            joined = " e ".join(parsed.targets)
            return f"Abrindo {joined} agora."

        if parsed.action == "close":
            MacDesktopController.close_multiple_apps(parsed.targets)
            joined = " e ".join(parsed.targets)
            return f"Fechando {joined} agora."

        if parsed.action == "search":
            query = parsed.targets[0]
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            return f"Pesquisando isso pra você: {query}"

        if parsed.action == "url":
            webbrowser.open(parsed.targets[0])
            return f"Abrindo {parsed.targets[0]}"

        return None