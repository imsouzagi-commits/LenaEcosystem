from __future__ import annotations

import queue
import threading
from typing import TYPE_CHECKING

from openjarvis.lena.boot_logger import LenaBootLogger
from openjarvis.lena.learned_patterns import LenaLearnedPatterns
from openjarvis.lena.learned_responses import LenaLearnedResponses

if TYPE_CHECKING:
    from openjarvis.agent.lena_agent import LenaAgent


class LenaLearningRuntime:
    _queue: "queue.Queue[tuple[LenaAgent, str]]" = queue.Queue()
    _io_lock = threading.RLock()
    _started = False

    @classmethod
    def boot(cls) -> None:
        if cls._started:
            return

        worker = threading.Thread(target=cls._worker_loop, daemon=True, name="lena-learning-runtime")
        worker.start()
        cls._started = True
        LenaBootLogger.write("learning runtime booted")

    @classmethod
    def enqueue(cls, agent: "LenaAgent", user_text: str) -> None:
        cls.boot()
        cls._queue.put((agent, user_text))

    @classmethod
    def learned_io_lock(cls) -> threading.RLock:
        return cls._io_lock

    @classmethod
    def reload_semantic_banks(cls, memory_engine) -> None:
        with memory_engine._lock:
            with cls._io_lock:
                memory_engine.learned_patterns = LenaLearnedPatterns.load()
                memory_engine.learned_responses = LenaLearnedResponses.load()

    @classmethod
    def _worker_loop(cls) -> None:
        from openjarvis.lena.conversation_learner import LenaConversationLearner

        while True:
            agent, user_text = cls._queue.get()

            try:
                LenaBootLogger.write(f"learning runtime processing: {user_text}")
                learned = LenaConversationLearner.learn(agent, user_text)

                if learned:
                    cls.reload_semantic_banks(agent.memory_engine)
                    LenaBootLogger.write("learning runtime semantic banks reloaded")
            except Exception as exc:
                LenaBootLogger.write(f"learning runtime failed: {type(exc).__name__}: {exc}")
            finally:
                cls._queue.task_done()
