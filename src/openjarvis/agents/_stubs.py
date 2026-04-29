from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, cast

from openjarvis.core.config import load_config
from openjarvis.core.events import EventBus, EventType
from openjarvis.core.types import Conversation, Message, Role, ToolResult
from openjarvis.engine._stubs import InferenceEngine

if TYPE_CHECKING:
    from openjarvis.tools._stubs import BaseTool

@dataclass(slots=True)
class AgentContext:
    """Runtime context handed to an agent on each invocation."""

    conversation: Conversation = field(default_factory=Conversation)
    tools: List[str] = field(default_factory=list)
    memory_results: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentResult:
    """Result returned after an agent completes a run."""

    content: str
    tool_results: List[ToolResult] = field(default_factory=list)
    turns: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """Base class for all agent implementations."""

    agent_id: str
    accepts_tools: bool = False

    _temperature: float
    _max_tokens: int
    _prompt_builder: Any | None
    _bus: EventBus | None
    _engine: InferenceEngine
    _model: str

    def __init__(
        self,
        engine: InferenceEngine,
        model: str,
        *,
        bus: Optional[EventBus] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        prompt_builder: Optional[Any] = None,
    ) -> None:
        self._engine = engine
        self._model = model
        self._bus = bus
        self._prompt_builder = prompt_builder

        if temperature is not None and max_tokens is not None:
            self._temperature = float(temperature)
            self._max_tokens = int(max_tokens)
            return

        try:
            cfg = load_config()
            self._temperature = float(
                temperature if temperature is not None else cfg.intelligence.temperature
            )
            self._max_tokens = int(
                max_tokens if max_tokens is not None else cfg.intelligence.max_tokens
            )
        except Exception:
            self._temperature = float(
                temperature
                if temperature is not None
                else getattr(self, "_default_temperature", 0.7)
            )
            self._max_tokens = int(
                max_tokens
                if max_tokens is not None
                else getattr(self, "_default_max_tokens", 1024)
            )

    def _emit_turn_start(self, input: str) -> None:
        if self._bus:
            self._bus.publish(
                EventType.AGENT_TURN_START,
                {"agent": self.agent_id, "input": input},
            )

    def _emit_turn_end(self, **data: Any) -> None:
        if self._bus:
            payload: Dict[str, Any] = {"agent": self.agent_id}
            payload.update(data)
            self._bus.publish(EventType.AGENT_TURN_END, payload)

    def _build_messages(
        self,
        input: str,
        context: Optional[AgentContext] = None,
        *,
        system_prompt: Optional[str] = None,
    ) -> List[Message]:
        messages: List[Message] = []

        context_has_system = bool(
            context
            and context.conversation.messages
            and any(m.role == Role.SYSTEM for m in context.conversation.messages)
        )

        effective_system_prompt: str | None = None

        if self._prompt_builder is not None:
            effective_system_prompt = cast(str, self._prompt_builder.build())
        elif system_prompt:
            effective_system_prompt = system_prompt
        elif not context_has_system:
            try:
                cfg = load_config()
                effective_system_prompt = cfg.agent.default_system_prompt or None
            except Exception:
                effective_system_prompt = None

        if effective_system_prompt:
            messages.append(Message(role=Role.SYSTEM, content=effective_system_prompt))

        if context and context.conversation.messages:
            messages.extend(context.conversation.messages)

        messages.append(Message(role=Role.USER, content=input))
        return messages

    def _generate(self, messages: List[Message], **extra_kwargs: Any) -> Dict[str, Any]:
        if self._bus and not getattr(self._engine, "_publishes_events", False):
            engine_id = getattr(self._engine, "engine_id", "")
            self._bus.publish(
                EventType.INFERENCE_START,
                {"model": self._model, "engine": engine_id},
            )

        result = cast(
            Dict[str, Any],
            self._engine.generate(
                messages,
                model=self._model,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
                **extra_kwargs,
            ),
        )

        if self._bus and not getattr(self._engine, "_publishes_events", False):
            usage = result.get("usage", {})
            self._bus.publish(
                EventType.INFERENCE_END,
                {
                    "model": self._model,
                    "usage": usage,
                    "content": result.get("content", ""),
                    "tool_calls": result.get("tool_calls", []),
                    "finish_reason": result.get("finish_reason", ""),
                },
            )

        return result

    def _max_turns_result(
        self,
        tool_results: List[ToolResult],
        turns: int,
        content: str = "",
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        self._emit_turn_end(turns=turns, max_turns_exceeded=True)

        md: Dict[str, Any] = {"max_turns_exceeded": True}
        if metadata:
            md.update(metadata)

        return AgentResult(
            content=content or "Maximum turns reached without a final answer.",
            tool_results=tool_results,
            turns=turns,
            metadata=md,
        )

    def _check_continuation(
        self,
        result: Dict[str, Any],
        messages: List[Message],
        *,
        max_continuations: int = 2,
    ) -> str:
        content = str(result.get("content", ""))
        finish_reason = str(result.get("finish_reason", ""))

        for _ in range(max_continuations):
            if finish_reason != "length":
                break

            messages.append(Message(role=Role.ASSISTANT, content=content))
            messages.append(
                Message(
                    role=Role.USER,
                    content="Continue from where you left off.",
                ),
            )

            cont = self._generate(messages)
            continuation = str(cont.get("content", ""))
            content += continuation
            finish_reason = str(cont.get("finish_reason", ""))

        return content

    @staticmethod
    def _strip_think_tags(text: str) -> str:
        text = re.sub(
            r"<think>.*?</think>\s*",
            "",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
        text = re.sub(r"^.*?</think>\s*", "", text, flags=re.DOTALL | re.IGNORECASE)
        return text.strip()

    @abstractmethod
    def run(
        self,
        input: str,
        context: Optional[AgentContext] = None,
        **kwargs: Any,
    ) -> AgentResult:
        ...

class ToolUsingAgent(BaseAgent):
    accepts_tools: bool = True

    _tools: List[Any]
    _executor: Any
    _max_turns: int
    _loop_guard: Any | None
    _skill_few_shot_examples: List[str]

    def __init__(
        self,
        engine: InferenceEngine,
        model: str,
        *,
        tools: Optional[List[BaseTool]] = None,
        bus: Optional[EventBus] = None,
        max_turns: Optional[int] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        loop_guard_config: Optional[Any] = None,
        capability_policy: Optional[Any] = None,
        agent_id: Optional[str] = None,
        interactive: bool = False,
        confirm_callback: Optional[Any] = None,
        skill_few_shot_examples: Optional[List[str]] = None,
    ) -> None:

        super().__init__(
            engine,
            model,
            bus=bus,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        from openjarvis.tools._stubs import ToolExecutor

        self._tools = list(tools or [])
        self._skill_few_shot_examples = list(skill_few_shot_examples or [])

        _aid = agent_id or getattr(self, "agent_id", "")

        self._executor = ToolExecutor(
            self._tools,
            bus=bus,
            capability_policy=capability_policy,
            agent_id=_aid,
            interactive=interactive,
            confirm_callback=confirm_callback,
        )

        if max_turns is not None:
            self._max_turns = int(max_turns)
        else:
            try:
                cfg = load_config()
                self._max_turns = int(cfg.agent.max_turns)
            except Exception:
                self._max_turns = int(getattr(self, "_default_max_turns", 10))

        self._loop_guard = None

        try:
            from openjarvis.agents.loop_guard import LoopGuard, LoopGuardConfig

            if loop_guard_config is None:
                loop_guard_config = LoopGuardConfig()
            elif isinstance(loop_guard_config, dict):
                loop_guard_config = LoopGuardConfig(**loop_guard_config)

            if loop_guard_config.enabled:
                self._loop_guard = LoopGuard(loop_guard_config, bus=bus)

        except ImportError:
            self._loop_guard = None


__all__ = ["AgentContext", "AgentResult", "BaseAgent", "ToolUsingAgent"]