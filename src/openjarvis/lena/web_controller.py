from __future__ import annotations

import subprocess
from urllib.parse import quote_plus

from openjarvis.lena.action_guard import LenaActionGuard


class LenaWebController:
    OPEN_PREFIXES = (
        "abre site ",
        "abrir site ",
        "abrir url ",
    )

    SEARCH_PREFIXES = (
        "pesquisa no google ",
        "pesquisar no google ",
        "busca no google ",
    )

    @staticmethod
    def execute_open(user_text: str) -> str:
        url = user_text.strip()
        lowered = url.lower()

        for prefix in LenaWebController.OPEN_PREFIXES:
            if lowered.startswith(prefix):
                url = url[len(prefix):].strip()
                break

        if not url:
            return "me diz qual site abrir."

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        allowed, _ = LenaActionGuard.allow("open_url", url)
        if not allowed:
            return "url bloqueada por segurança."

        try:
            subprocess.run(
                ["open", "-a", "Safari", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
                timeout=8,
            )
            return f"abri {url}"
        except Exception:
            return f"não consegui abrir {url}"

    @staticmethod
    def execute_search(lowered: str, user_text: str) -> str:
        query = user_text.strip()
        lowered_query = query.lower()

        for prefix in LenaWebController.SEARCH_PREFIXES:
            if lowered_query.startswith(prefix):
                query = query[len(prefix):].strip()
                break

        if not query:
            return "me diz o que pesquisar."

        url = f"https://www.google.com/search?q={quote_plus(query)}"

        try:
            subprocess.run(
                ["open", "-a", "Safari", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
                timeout=8,
            )
            return f"pesquisando {query}"
        except Exception:
            return f"não consegui pesquisar {query}"
