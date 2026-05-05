from __future__ import annotations

import logging
import threading
import traceback
from typing import Any, Callable

from openjarvis.lena.boot_logger import LenaBootLogger

logger = logging.getLogger(__name__)


def _report_thread_crash(name: str, exc: BaseException) -> None:
    message = f"THREAD CRASH [{name}] {exc}"
    try:
        LenaBootLogger.write(message)
        LenaBootLogger.write(traceback.format_exc())
    except Exception:
        pass
    logger.exception(message)


class SafeDaemonThread(threading.Thread):
    def __init__(
        self,
        *,
        target: Callable[..., Any],
        name: str,
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            target=self._runner,
            name=name,
            daemon=True,
        )
        self._real_target = target
        self._real_args = args
        self._real_kwargs = kwargs or {}

    def _runner(self) -> None:
        try:
            self._real_target(*self._real_args, **self._real_kwargs)
        except Exception as exc:
            _report_thread_crash(self.name, exc)


def run_guarded_background(
    name: str,
    target: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> SafeDaemonThread:
    t = SafeDaemonThread(
        target=target,
        name=name,
        args=args,
        kwargs=kwargs,
    )
    t.start()
    return t
