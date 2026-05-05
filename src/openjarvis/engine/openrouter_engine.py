from __future__ import annotations

import os
import time
from typing import Any, Dict, List

import httpx


class OpenRouterEngine:
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    FREE_MODELS = [
        "mistralai/mistral-7b-instruct:free",
        "google/gemma-2-9b-it:free",
        "nousresearch/hermes-3-llama-3.1-8b:free",
        "meta-llama/llama-3.2-3b-instruct:free",
    ]

    def __init__(self, model: str | None = None) -> None:
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.model = model

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def _request_model(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "OpenLena",
        }

        payload: Dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(self.BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.6,
        max_tokens: int = 500,
    ) -> str:
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY missing")

        models = [self.model] if self.model else self.FREE_MODELS

        last_exc: Exception | None = None

        for model_name in models:
            try:
                return self._request_model(
                    model_name,
                    messages,
                    temperature,
                    max_tokens,
                )
            except Exception as exc:
                last_exc = exc
                time.sleep(0.8)
                continue

        raise RuntimeError(f"All OpenRouter free models failed: {last_exc}")
