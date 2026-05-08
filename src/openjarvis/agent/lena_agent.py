from __future__ import annotations

import asyncio
import time
from typing import Any, AsyncGenerator, Dict, Generator, List

from openjarvis.lena.runtime.dependencies import LenaDependencies
from openjarvis.lena.fallback_controller import LenaFallbackController
from openjarvis.lena.intent_dispatcher import LenaIntentDispatcher
from openjarvis.lena.unified_route_resolver import UnifiedRouteResolver
from openjarvis.lena.memory_facade import LenaMemoryFacade
from openjarvis.lena.cognitive_orchestrator import LenaCognitiveOrchestrator
from openjarvis.lena.action_orchestrator import LenaActionOrchestrator
from openjarvis.lena.conversation_orchestrator import LenaConversationOrchestrator
from openjarvis.lena.conversation_learner import LenaConversationLearner
from openjarvis.lena.task_orchestrator import LenaTaskOrchestrator
from openjarvis.lena.learning_runtime import LenaLearningRuntime
from openjarvis.lena.turn_manager import LenaTurnManager
from openjarvis.lena.cognition.semantic_packet_builder import LenaSemanticPacketBuilder
from openjarvis.lena.observability.semantic_trace import LenaSemanticTrace
from openjarvis.lena.narrative_tension_engine import LenaNarrativeTensionEngine


class LenaAgent:
    KERNEL_READY_ROUTES = {
        "DESKTOP",
        "FILE_OP",
        "WEB_SEARCH",
        "WEB_OPEN",
    }

    def __init__(self) -> None:
        self.kernel = (
            LenaDependencies.LenaKernel()
            if LenaDependencies.LenaKernel
            else None
        )

        self.memory_engine = LenaMemoryFacade()

        self.desktop_controller = (
            LenaDependencies.LenaDesktopController(self.kernel)
            if LenaDependencies.LenaDesktopController and self.kernel
            else None
        )

        self.file_controller = (
            LenaDependencies.LenaFileController(self.kernel)
            if LenaDependencies.LenaFileController and self.kernel
            else None
        )

        self.searcher = (
            LenaDependencies.LenaSearchOrchestrator()
            if LenaDependencies.LenaSearchOrchestrator
            else None
        )

        self.fallback_controller = LenaFallbackController()
        self.cognitive = LenaCognitiveOrchestrator()
        self.actioner = LenaActionOrchestrator()
        self.conversationer = LenaConversationOrchestrator()
        self.learner = LenaConversationLearner()
        self.turn_manager = LenaTurnManager(self.memory_engine)

        self.last_route = "BOOT"
        self.last_route_used = "BOOT"
        self.last_latency_ms = 0.0

    def _extract_user_text(
        self,
        messages: List[Dict[str, Any]],
    ) -> str:
        for message in reversed(messages):
            if message.get("role") == "user":
                return str(message.get("content", ""))
        return ""

    def _fast_return(
        self,
        content: str,
    ) -> Dict[str, Any]:
        return {
            "id": f"lena-{int(time.time())}",
            "object": "chat.completion",
            "route": self.last_route,
            "route_used": self.last_route_used,
            "latency_ms": self.last_latency_ms,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content,
                    },
                    "finish_reason": "stop",
                }
            ],
        }

    def _requires_kernel_ready(
        self,
        routes: set[str],
    ) -> bool:
        return bool(
            self.kernel
            and routes & self.KERNEL_READY_ROUTES
        )

    def run(
        self,
        messages: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        started = time.perf_counter()
        user_text = self._extract_user_text(messages)

        if self.memory_engine.needs_learning(
            user_text.lower().strip()
        ):
            LenaLearningRuntime.enqueue(self, user_text)

        split_commands = LenaTaskOrchestrator.split(user_text)
        classified_commands = []

        for command in split_commands:
            cognitive = self.cognitive.classify(
                command,
                self.memory_engine,
            )
            route = UnifiedRouteResolver.resolve(cognitive)
            classified_commands.append(
                (command, route, cognitive)
            )

        planned_routes = {
            route
            for _, route, _ in classified_commands
        }

        self.last_route = (
            "TASK_CHAIN"
            if len(classified_commands) > 1
            else next(iter(planned_routes))
        )

        self.last_route_used = self.last_route

        dominant = None

        if classified_commands:
            dominant = max(
                (c for _, _, c in classified_commands),
                key=lambda c: {
                    "semantic_relational": 100,
                    "practical": 80,
                    "factual": 70,
                    "social": 40,
                    "neutral": 10,
                }.get(c.domain, 0),
            )

        self.memory_engine._last_cognitive = dominant

        self.memory_engine.ingest_user_turn(
            user_text,
            self.last_route,
        )

        packet = self.memory_engine.finalize_user_semantic_turn(
            user_text,
            self.last_route,
        )

        packet = LenaSemanticPacketBuilder.enrich(
            packet,
            self.memory_engine,
            user_text,
        )

        LenaNarrativeTensionEngine.ingest_user(
            self.memory_engine,
            user_text,
            packet,
        )

        if self._requires_kernel_ready(planned_routes):
            assert self.kernel is not None

            if not self.kernel.await_ready(timeout=5.0):
                self.last_latency_ms = round(
                    (time.perf_counter() - started) * 1000,
                    3,
                )
                return self._fast_return(
                    "kernel Lena ainda está inicializando."
                )

        executed = []

        for command, route, cognitive in classified_commands:
            if route == "LOCAL_SEARCH":
                payload = (
                    self.searcher.local_search(command)
                    if self.searcher
                    else []
                )

                tool_payload = (
                    "não encontrei nada útil localmente"
                    if not payload
                    else payload[0]
                )

                response = self.conversationer.respond(
                    self,
                    command,
                    cognitive=cognitive,
                    tool_payload=tool_payload,
                    semantic_packet=packet,
                )

            elif route == "WEB_SEARCH_BG":
                tool_payload = (
                    self.searcher.web_search(command)
                    if self.searcher
                    else "search unavailable"
                )

                response = self.conversationer.respond(
                    self,
                    command,
                    cognitive=cognitive,
                    tool_payload=tool_payload,
                    semantic_packet=packet,
                )

            else:
                response = LenaIntentDispatcher.dispatch(
                    self,
                    route,
                    command,
                    cognitive=cognitive,
                    semantic_packet=packet,
                )

            executed.append((route, response or "certo."))

        final_response = " | ".join(
            resp for _, resp in executed
        )

        executed_routes = {
            r for r, _ in executed
        }

        self.last_route_used = (
            self.last_route
            if len(executed_routes) > 1
            else next(iter(executed_routes))
        )

        final_response = self.turn_manager.finalize_turn(
            user_text,
            final_response,
            packet,
        )

        self.last_latency_ms = round(
            (time.perf_counter() - started) * 1000,
            3,
        )

        return self._fast_return(final_response)

    def run_stream(
        self,
        messages: List[Dict[str, Any]],
    ) -> Generator[str, None, None]:
        yield self.run(messages)["choices"][0]["message"]["content"]

    async def run_stream_async(
        self,
        messages: List[Dict[str, Any]],
    ) -> AsyncGenerator[str, None]:
        for chunk in self.run_stream(messages):
            yield (
                "data: "
                + str(
                    {
                        "route": self.last_route,
                        "route_used": self.last_route_used,
                        "latency_ms": self.last_latency_ms,
                        "choices": [
                            {
                                "delta": {"content": chunk},
                                "index": 0,
                                "finish_reason": None,
                            }
                        ],
                    }
                )
                + "\n\n"
            )
            await asyncio.sleep(0.15)
