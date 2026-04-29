"""Cloud inference engine — Lena unified smart cloud core."""

from __future__ import annotations

import importlib
import json
import logging
import os
import time
from collections.abc import AsyncIterator, Sequence
from typing import Any, Callable, Dict, List, Tuple

import httpx

from openjarvis.core.registry import EngineRegistry
from openjarvis.core.types import Message, Role
from openjarvis.engine._base import EngineConnectionError, InferenceEngine, messages_to_dicts
from openjarvis.engine._stubs import StreamChunk

logger = logging.getLogger(__name__)


def _coerce_runtime_args(model: Any, temperature: Any, max_tokens: Any) -> tuple[str, float, int]:
    return str(model), float(temperature), int(max_tokens)


PRICING: Dict[str, tuple[float, float]] = {
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-5": (10.00, 30.00),
    "gpt-5.4": (15.00, 60.00),
    "gpt-5-mini": (0.25, 2.00),
    "o3-mini": (1.10, 4.40),
    "claude-sonnet-4-20250514": (3.00, 15.00),
    "claude-opus-4-20250514": (15.00, 75.00),
    "claude-haiku-3-5-20241022": (0.80, 4.00),
    "claude-opus-4-6": (5.00, 25.00),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-haiku-4-5-20251001": (1.00, 5.00),
    "gemini-2.5-pro": (1.25, 10.00),
    "gemini-2.5-flash": (0.30, 2.50),
    "gemini-3-pro": (2.00, 12.00),
    "gemini-3-flash": (0.50, 3.00),
    "gemini-3.1-pro-preview": (2.50, 15.00),
    "gemini-3.1-flash-lite-preview": (0.30, 2.50),
    "gemini-3-flash-preview": (0.50, 3.00),
    "MiniMax-M2.7": (0.30, 1.20),
    "MiniMax-M2.7-highspeed": (0.60, 2.40),
    "MiniMax-M2.5": (0.30, 1.20),
    "MiniMax-M2.5-highspeed": (0.60, 2.40),
}

_AZURE_OPENAI_ENDPOINT = "https://thiago4774w94.openai.azure.com/"
_AZURE_OPENAI_API_VERSION = "2025-01-01-preview"
_AZURE_OPENAI_DEFAULT_DEPLOYMENT = "gpt-4.1"

_AZURE_MODELS = [_AZURE_OPENAI_DEFAULT_DEPLOYMENT]

_ANTHROPIC_MODELS = [
    "claude-sonnet-4-20250514",
    "claude-opus-4-20250514",
    "claude-haiku-3-5-20241022",
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-haiku-4-5",
    "claude-haiku-4-5-20251001",
]

_GOOGLE_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-3-pro",
    "gemini-3-flash",
]

_MINIMAX_MODELS = [
    "MiniMax-M2.7",
    "MiniMax-M2.7-highspeed",
    "MiniMax-M2.5",
    "MiniMax-M2.5-highspeed",
]

_OPENROUTER_POPULAR = [
    "openrouter/auto",
    "openrouter/openai/gpt-4o",
    "openrouter/anthropic/claude-sonnet-4",
]

_CODEX_MODELS = [
    "codex/gpt-4o",
    "codex/gpt-4o-mini",
    "codex/o3-mini",
    "codex/gpt-5-mini",
]

SYSTEM_PROMPT_LENA = """
Você é Lena.
Você fala como uma pessoa inteligente, natural e objetiva.
Nunca seja robótica.
Nunca use frases genéricas.
""".strip()


def _is_minimax_model(model: str) -> bool:
    return model.lower().startswith("minimax")


def _is_openrouter_model(model: str) -> bool:
    return model.startswith("openrouter/")


def _is_codex_model(model: str) -> bool:
    return model.startswith("codex/")


def _is_anthropic_model(model: str) -> bool:
    return "claude" in model.lower() and not _is_openrouter_model(model)


def _is_google_model(model: str) -> bool:
    return "gemini" in model.lower() and not _is_openrouter_model(model)


def _is_openai_reasoning_model(model: str) -> bool:
    m = model.lower()
    return m.startswith(("o1", "o3")) or m.startswith("gpt-5-mini")


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    prices = PRICING.get(model)

    if prices is None:
        for key, value in PRICING.items():
            if model.startswith(key):
                prices = value
                break

    if prices is None:
        return 0.0

    return ((prompt_tokens / 1_000_000) * prices[0]) + ((completion_tokens / 1_000_000) * prices[1])


def _convert_tools_to_anthropic(openai_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    converted: List[Dict[str, Any]] = []

    for tool in openai_tools:
        func = tool.get("function", {})
        converted.append(
            {
                "name": func.get("name", ""),
                "description": func.get("description", ""),
                "input_schema": func.get("parameters", {}),
            }
        )

    return converted


@EngineRegistry.register("cloud")
class CloudEngine(InferenceEngine):
    engine_id = "cloud"
    is_cloud = True

    def __init__(self) -> None:
        self._azure_openai_client: Any = None
        self._anthropic_client: Any = None
        self._google_client: Any = None
        self._openrouter_client: Any = None
        self._minimax_client: Any = None
        self._codex_client: Any = None
        self._init_clients()

    def _log_route(self, route: str, model: str) -> None:
        print(f"[ROUTE={route}] [MODEL={model}]")

    def _safe_provider_call(self, fn: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
        try:
            return fn()
        except Exception as exc:
            logger.exception("Cloud provider failure: %s", exc)
            return {
                "content": "Tive uma falha momentânea pra pensar isso. Me manda de novo.",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "model": "fallback",
                "finish_reason": "error",
                "cost_usd": 0.0,
            }

    def _init_clients(self) -> None:
        api_key = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

        if api_key:
            try:
                from openai import AzureOpenAI
                self._azure_openai_client = AzureOpenAI(
                    api_key=api_key,
                    api_version=_AZURE_OPENAI_API_VERSION,
                    azure_endpoint=_AZURE_OPENAI_ENDPOINT,
                )
            except Exception:
                logger.warning("Azure OpenAI unavailable")

        if os.environ.get("ANTHROPIC_API_KEY"):
            try:
                import anthropic
                self._anthropic_client = anthropic.Anthropic()
            except Exception:
                logger.warning("Anthropic unavailable")

        if os.environ.get("OPENROUTER_API_KEY"):
            try:
                import openai
                self._openrouter_client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=os.environ["OPENROUTER_API_KEY"],
                )
            except Exception:
                logger.warning("OpenRouter unavailable")

    def _inject_lena_system(self, messages: Sequence[Message]) -> List[Message]:
        prepared = list(messages)

        if not prepared or prepared[0].role != Role.SYSTEM:
            prepared.insert(0, Message(role=Role.SYSTEM, content=SYSTEM_PROMPT_LENA))
            return prepared

        prepared[0] = Message(
            role=Role.SYSTEM,
            content=SYSTEM_PROMPT_LENA + "\n\n" + prepared[0].content,
        )
        return prepared

    def _prepare_anthropic_messages(self, messages: Sequence[Message]) -> Tuple[str, List[Dict[str, Any]]]:
        system_text = ""
        chat_msgs: List[Dict[str, Any]] = []

        for m in messages:
            if m.role == Role.SYSTEM:
                system_text = m.content
            else:
                chat_msgs.append({"role": m.role.value, "content": m.content})

        return system_text, chat_msgs

    @staticmethod
    def _codex_build_input(messages: Sequence[Message]) -> tuple[str, List[Dict[str, Any]]]:
        instructions = ""
        input_msgs: List[Dict[str, Any]] = []

        for m in messages:
            if m.role == Role.SYSTEM:
                instructions = m.content
            elif m.role in (Role.USER, Role.ASSISTANT):
                input_msgs.append(
                    {
                        "role": m.role.value,
                        "content": [{"type": "input_text", "text": m.content}],
                    }
                )

        return instructions, input_msgs

    def _generate_codex(self, messages: Sequence[Message], *, model: str, temperature: float, max_tokens: int, **kwargs: Any) -> Dict[str, Any]:
        raise EngineConnectionError("Codex desabilitado nesta sprint")

    def _generate_openai(self, messages: Sequence[Message], *, model: str, temperature: float, max_tokens: int, **kwargs: Any) -> Dict[str, Any]:
        if self._azure_openai_client is None:
            raise EngineConnectionError("Azure OpenAI client not available")

        self._log_route("AZURE_OPENAI", model)

        prepared_messages = self._inject_lena_system(messages)

        create_kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages_to_dicts(prepared_messages),
            "max_completion_tokens": max_tokens,
            **kwargs,
        }

        if not _is_openai_reasoning_model(model):
            create_kwargs["temperature"] = temperature

        t0 = time.monotonic()
        resp = self._azure_openai_client.chat.completions.create(**create_kwargs)
        elapsed = time.monotonic() - t0

        choice = resp.choices[0]
        usage = resp.usage

        return {
            "content": choice.message.content or "",
            "usage": {
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "total_tokens": usage.total_tokens if usage else 0,
            },
            "model": model,
            "finish_reason": choice.finish_reason or "stop",
            "cost_usd": estimate_cost(model, usage.prompt_tokens if usage else 0, usage.completion_tokens if usage else 0),
            "ttft": elapsed,
        }

    def _generate_openrouter(self, messages: Sequence[Message], *, model: str, temperature: float, max_tokens: int, **kwargs: Any) -> Dict[str, Any]:
        if self._openrouter_client is None:
            raise EngineConnectionError("OpenRouter unavailable")

        actual_model = model.removeprefix("openrouter/")
        self._log_route("OPENROUTER", actual_model)

        prepared_messages = self._inject_lena_system(messages)

        resp = self._openrouter_client.chat.completions.create(
            model=actual_model,
            messages=messages_to_dicts(prepared_messages),
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

        choice = resp.choices[0]

        return {
            "content": choice.message.content or "",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "model": actual_model,
            "finish_reason": choice.finish_reason or "stop",
        }

    def _generate_anthropic(self, messages: Sequence[Message], *, model: str, temperature: float, max_tokens: int, **kwargs: Any) -> Dict[str, Any]:
        raise EngineConnectionError("Anthropic disabled nessa sprint")

    def _generate_google(self, messages: Sequence[Message], *, model: str, temperature: float, max_tokens: int, **kwargs: Any) -> Dict[str, Any]:
        raise EngineConnectionError("Google disabled nessa sprint")

    async def _yield_tokens_from_generate(
        self,
        generator_func: Callable[..., Dict[str, Any]],
        messages: Sequence[Message],
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        result = generator_func(messages, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)
        text = str(result.get("content", ""))

        for token in text.split():
            yield token + " "

    async def _stream_openai(self, messages: Sequence[Message], *, model: str, temperature: float, max_tokens: int, **kwargs: Any) -> AsyncIterator[str]:
        async for token in self._yield_tokens_from_generate(self._generate_openai, messages, model, temperature, max_tokens, **kwargs):
            yield token

    async def _stream_full_openai(self, messages: Sequence[Message], *, model: str, temperature: float, max_tokens: int, **kwargs: Any) -> AsyncIterator[StreamChunk]:
        async for token in self._stream_openai(messages, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs):
            yield StreamChunk(content=token)

    def generate(self, messages: Sequence[Message], model: str, temperature: float = 0.35, max_tokens: int = 1024, **kwargs: Any) -> Dict[str, Any]:
        model, temperature, max_tokens = _coerce_runtime_args(model, temperature, max_tokens)

        if _is_openrouter_model(model):
            return self._safe_provider_call(
                lambda: self._generate_openrouter(messages, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)
            )

        return self._safe_provider_call(
            lambda: self._generate_openai(messages, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)
        )

    async def stream_generate(self, messages: Sequence[Message], model: str, temperature: float = 0.35, max_tokens: int = 1024, **kwargs: Any) -> AsyncIterator[str]:
        async for item in self._stream_openai(messages, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs):
            yield item

    async def stream_generate_full(
        self,
        messages: Sequence[Message],
        model: str,
        temperature: float = 0.35,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        async for chunk in self._stream_full_openai(messages, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs):
            yield chunk

    async def stream(
        self,
        messages: Sequence[Message],
        model: str,
        temperature: float = 0.35,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        async for item in self.stream_generate(messages, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs):
            yield item

    def list_models(self) -> List[str]:
        models: List[str] = []

        if self._azure_openai_client is not None:
            models.extend(_AZURE_MODELS)
        if self._openrouter_client is not None:
            models.extend(_OPENROUTER_POPULAR)

        return models

    def health(self) -> bool:
        return self._azure_openai_client is not None or self._openrouter_client is not None

    def close(self) -> None:
        for attr in ["_azure_openai_client", "_openrouter_client"]:
            client = getattr(self, attr, None)

            if client and hasattr(client, "close"):
                try:
                    client.close()
                except Exception:
                    pass

            setattr(self, attr, None)


__all__ = ["CloudEngine", "PRICING", "estimate_cost"]