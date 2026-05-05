from __future__ import annotations

import os
from typing import Any, Dict, List

import httpx


class AzureOpenAIEngine:
    API_VERSION = "2025-01-01-preview"

    def __init__(self) -> None:
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
        self.fast_deployment = os.getenv("AZURE_OPENAI_FAST_DEPLOYMENT", "").strip()

    @property
    def available(self) -> bool:
        return bool(self.endpoint and self.api_key and self.fast_deployment)

    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.4,
        max_tokens: int = 48,
        timeout: float = 1.25,
    ) -> str:
        if not self.available:
            raise RuntimeError("Azure OpenAI not configured")

        url = (
            f"{self.endpoint}/openai/deployments/{self.fast_deployment}/chat/completions"
            f"?api-version={self.API_VERSION}"
        )

        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
