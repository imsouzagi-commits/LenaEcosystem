# /tests/memory/test_context.py

"""Tests for context injection."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from openjarvis.core.events import EventBus, EventType
from openjarvis.core.types import Message, Role
from openjarvis.tools.storage._stubs import MemoryBackend, RetrievalResult
from openjarvis.tools.storage.context import (
    ContextConfig,
    build_context_message,
    format_context,
    inject_context,
)


class _FakeMemory(MemoryBackend):
    """In-memory backend that returns pre-set results."""

    backend_id = "fake"

    def __init__(
        self,
        results: Optional[List[RetrievalResult]] = None,
        should_fail: bool = False,
    ) -> None:
        self._results = results or []
        self._should_fail = should_fail
        self.last_top_k: Optional[int] = None
        self.last_query: Optional[str] = None

    def store(
        self,
        content: str,
        *,
        source: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        return uuid.uuid4().hex

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        if self._should_fail:
            raise RuntimeError("backend retrieval failure")
        self.last_query = query
        self.last_top_k = top_k
        return self._results[:top_k]

    def delete(self, doc_id: str) -> bool:
        return False

    def clear(self) -> None:
        self._results.clear()


def test_format_context_with_sources():
    results = [
        RetrievalResult(content="Python is great", score=1.0, source="wiki.md"),
        RetrievalResult(content="Java is verbose", score=0.8, source="notes.txt"),
    ]
    text = format_context(results)
    assert "[Source: wiki.md]" in text
    assert "[Source: notes.txt]" in text
    assert "Python is great" in text
    assert "Java is verbose" in text


def test_format_context_empty():
    assert format_context([]) == ""


def test_build_context_message_role():
    results = [
        RetrievalResult(content="test", score=1.0, source="s.md"),
    ]
    msg = build_context_message(results)
    assert msg.role == Role.SYSTEM
    assert "knowledge base" in msg.content.lower()
    assert "test" in msg.content


def test_inject_context_adds_system_message():
    results = [
        RetrievalResult(content="relevant info", score=0.9, source="doc.md"),
    ]
    backend = _FakeMemory(results)
    messages = [Message(role=Role.USER, content="hello")]

    augmented = inject_context("query", messages, backend)

    assert len(augmented) == 2
    assert augmented[0].role == Role.SYSTEM
    assert "relevant info" in augmented[0].content


def test_inject_context_filters_low_score():
    results = [
        RetrievalResult(content="low score", score=0.01),
    ]
    backend = _FakeMemory(results)
    messages = [Message(role=Role.USER, content="hello")]
    cfg = ContextConfig(min_score=0.1)

    augmented = inject_context("query", messages, backend, config=cfg)

    assert len(augmented) == 1


def test_inject_context_respects_max_tokens():
    content = " ".join(f"word{i}" for i in range(100))
    results = [
        RetrievalResult(content=content, score=1.0, source="a.md"),
        RetrievalResult(content=content, score=0.9, source="b.md"),
    ]
    backend = _FakeMemory(results)
    messages = [Message(role=Role.USER, content="test")]
    cfg = ContextConfig(max_context_tokens=150)

    augmented = inject_context("query", messages, backend, config=cfg)

    assert len(augmented) == 2
    assert augmented[0].content.count("[Source:") == 1


def test_inject_context_disabled():
    results = [
        RetrievalResult(content="data", score=1.0),
    ]
    backend = _FakeMemory(results)
    messages = [Message(role=Role.USER, content="hello")]
    cfg = ContextConfig(enabled=False)

    augmented = inject_context("query", messages, backend, config=cfg)

    assert len(augmented) == 1


def test_inject_context_no_results_returns_original():
    backend = _FakeMemory([])
    messages = [Message(role=Role.USER, content="hello")]

    augmented = inject_context("query", messages, backend)

    assert augmented is messages


def test_inject_context_publishes_event():
    bus = EventBus(record_history=True)
    results = [
        RetrievalResult(content="info", score=0.9, source="s.md"),
    ]
    backend = _FakeMemory(results)
    messages = [Message(role=Role.USER, content="hello")]

    import openjarvis.tools.storage.context as mod

    original = mod.get_event_bus
    mod.get_event_bus = lambda: bus

    try:
        inject_context("query", messages, backend)
        events = [
            e for e in bus.history
            if e.event_type == EventType.MEMORY_RETRIEVE
        ]
        assert len(events) == 1
        assert events[0].data["context_injection"] is True
    finally:
        mod.get_event_bus = original


def test_inject_context_does_not_mutate_original():
    results = [
        RetrievalResult(content="info", score=0.9, source="s.md"),
    ]
    backend = _FakeMemory(results)
    messages = [Message(role=Role.USER, content="hello")]
    original_len = len(messages)

    augmented = inject_context("query", messages, backend)

    assert len(messages) == original_len
    assert len(augmented) == original_len + 1


def test_inject_context_passes_query_to_backend():
    results = [
        RetrievalResult(content="info", score=0.9),
    ]
    backend = _FakeMemory(results)
    messages = [Message(role=Role.USER, content="hello")]

    inject_context("what is python", messages, backend)

    assert backend.last_query == "what is python"


def test_inject_context_respects_top_k():
    results = [
        RetrievalResult(content=f"info {i}", score=1.0 - i * 0.1)
        for i in range(10)
    ]
    backend = _FakeMemory(results)
    messages = [Message(role=Role.USER, content="hello")]
    cfg = ContextConfig(top_k=3)

    inject_context("query", messages, backend, config=cfg)

    assert backend.last_top_k == 3


def test_inject_context_backend_failure_returns_original():
    backend = _FakeMemory(should_fail=True)
    messages = [Message(role=Role.USER, content="hello")]

    augmented = inject_context("query", messages, backend)

    assert augmented is messages


def test_inject_context_filters_multiple_low_scores():
    results = [
        RetrievalResult(content="bad1", score=0.01),
        RetrievalResult(content="bad2", score=0.05),
        RetrievalResult(content="good", score=0.9),
    ]
    backend = _FakeMemory(results)
    messages = [Message(role=Role.USER, content="hello")]
    cfg = ContextConfig(min_score=0.1)

    augmented = inject_context("query", messages, backend, config=cfg)

    assert len(augmented) == 2
    assert "good" in augmented[0].content
    assert "bad1" not in augmented[0].content
    assert "bad2" not in augmented[0].content


def test_inject_context_preserves_highest_ranked_results():
    results = [
        RetrievalResult(content="top", score=0.99, source="top.md"),
        RetrievalResult(content="mid", score=0.70, source="mid.md"),
        RetrievalResult(content="low", score=0.50, source="low.md"),
    ]
    backend = _FakeMemory(results)
    messages = [Message(role=Role.USER, content="hello")]

    augmented = inject_context("query", messages, backend)

    system_content = augmented[0].content
    assert "top" in system_content
    assert system_content.index("top") < system_content.index("mid")


def test_build_context_message_contains_all_entries():
    results = [
        RetrievalResult(content="alpha", score=1.0, source="a.md"),
        RetrievalResult(content="beta", score=0.9, source="b.md"),
    ]

    msg = build_context_message(results)

    assert "alpha" in msg.content
    assert "beta" in msg.content
    assert msg.content.count("[Source:") == 2


def test_format_context_without_sources():
    results = [
        RetrievalResult(content="plain memory", score=1.0),
    ]

    text = format_context(results)

    assert "plain memory" in text


def test_inject_context_with_all_filtered_results_returns_original():
    results = [
        RetrievalResult(content="x", score=0.01),
        RetrievalResult(content="y", score=0.02),
    ]
    backend = _FakeMemory(results)
    messages = [Message(role=Role.USER, content="hello")]
    cfg = ContextConfig(min_score=0.5)

    augmented = inject_context("query", messages, backend, config=cfg)

    assert augmented is messages