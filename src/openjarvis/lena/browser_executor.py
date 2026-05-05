from __future__ import annotations

import subprocess
from urllib.parse import quote_plus

from openjarvis.lena.action_guard import LenaActionGuard
from openjarvis.lena.job_center import LenaJobCenter
from openjarvis.lena.kernel import LenaKernel


class LenaBrowserExecutor:
    @staticmethod
    def search(kernel: LenaKernel, query: str) -> str:
        allowed, reason = LenaActionGuard.allow("open_url", query)
        if not allowed:
            return reason

        job_id = LenaJobCenter.start(kernel, "browser_search", query)

        try:
            url = f"https://www.google.com/search?q={quote_plus(query)}"
            subprocess.run(["open", "-a", "ChatGPT Atlas", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            LenaJobCenter.finish(kernel, job_id, "completed")
            return f"pesquisando {query} no Atlas."
        except Exception:
            LenaJobCenter.finish(kernel, job_id, "failed")
            return "não consegui abrir a pesquisa no Atlas."
