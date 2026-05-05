from __future__ import annotations

from typing import Any, Dict

import httpx


class OllamaEngine:
    BASE_URL = "http://127.0.0.1:11434/api/generate"

    FAST_MODEL = "phi4-mini:latest"
    REFLECT_MODEL = "phi4-mini:latest"

    def __init__(self) -> None:
        self._timeout = 8.0

    @property
    def available(self) -> bool:
        try:
            with httpx.Client(timeout=1.5) as client:
                r = client.get("http://127.0.0.1:11434/api/tags")
                return r.status_code == 200
        except Exception:
            return False

    def complete(
        self,
        prompt: str,
        *,
        reflective: bool = False,
        temperature: float = 0.55,
        max_tokens: int = 80,
    ) -> str:
        model = self.REFLECT_MODEL if reflective else self.FAST_MODEL

        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        timeout = httpx.Timeout(self._timeout, connect=2.0)

        with httpx.Client(timeout=timeout) as client:
            response = client.post(self.BASE_URL, json=payload)
            response.raise_for_status()
            data = response.json()

        return data.get("response", "").strip()
