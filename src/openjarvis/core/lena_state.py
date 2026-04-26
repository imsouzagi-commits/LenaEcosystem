from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any


STATE_PATH = Path.home() / ".lena_state.json"


class LenaStateManager:
    def __init__(self) -> None:
        self.mode: str = "idle"
        self.last_user_query: str = ""
        self.last_lena_response: str = ""
        self.last_opened_app: str = ""
        self.last_detected_intent: str = ""
        self.last_file_touched: str = ""
        self.last_folder_opened: str = ""
        self.pending_tasks: list[str] = []
        self.recent_actions: list[dict[str, Any]] = []
        self.active_session_id: str = "default"
        self.boot_time: str = datetime.now().isoformat()
        self.last_interaction: str = datetime.now().isoformat()
        self.load()

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "last_user_query": self.last_user_query,
            "last_lena_response": self.last_lena_response,
            "last_opened_app": self.last_opened_app,
            "last_detected_intent": self.last_detected_intent,
            "last_file_touched": self.last_file_touched,
            "last_folder_opened": self.last_folder_opened,
            "pending_tasks": self.pending_tasks,
            "recent_actions": self.recent_actions,
            "active_session_id": self.active_session_id,
            "boot_time": self.boot_time,
            "last_interaction": self.last_interaction,
        }

    def _save_worker(self) -> None:
        self.last_interaction = datetime.now().isoformat()
        try:
            STATE_PATH.write_text(
                json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as exc:
            print(f"[LENA STATE SAVE ERROR] {exc}")

    def save(self) -> None:
        threading.Thread(target=self._save_worker, daemon=True).start()

    def load(self) -> None:
        if not STATE_PATH.exists():
            self._save_worker()
            return

        try:
            data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            self.mode = data.get("mode", "idle")
            self.last_user_query = data.get("last_user_query", "")
            self.last_lena_response = data.get("last_lena_response", "")
            self.last_opened_app = data.get("last_opened_app", "")
            self.last_detected_intent = data.get("last_detected_intent", "")
            self.last_file_touched = data.get("last_file_touched", "")
            self.last_folder_opened = data.get("last_folder_opened", "")
            self.pending_tasks = data.get("pending_tasks", [])
            self.recent_actions = data.get("recent_actions", [])
            self.active_session_id = data.get("active_session_id", "default")
            self.boot_time = data.get("boot_time", datetime.now().isoformat())
            self.last_interaction = data.get(
                "last_interaction",
                datetime.now().isoformat(),
            )
        except Exception as exc:
            print(f"[LENA STATE LOAD ERROR] {exc}")
            self._save_worker()

    def register_action(
        self,
        query: str = "",
        response: str = "",
        intent: str = "",
        app: str = "",
        file_touched: str = "",
        folder_opened: str = "",
        mode: str | None = None,
    ) -> None:
        if query:
            self.last_user_query = query

        if response:
            self.last_lena_response = response

        if intent:
            self.last_detected_intent = intent

        if app:
            self.last_opened_app = app

        if file_touched:
            self.last_file_touched = file_touched

        if folder_opened:
            self.last_folder_opened = folder_opened

        if mode:
            self.mode = mode

        self.recent_actions.append(
            {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": response,
                "intent": intent,
                "app": app,
                "file_touched": file_touched,
                "folder_opened": folder_opened,
                "mode": self.mode,
            }
        )

        self.recent_actions = self.recent_actions[-40:]
        self.save()

    def add_task(self, task: str) -> None:
        self.pending_tasks.append(task)
        self.save()

    def remove_task(self, task: str) -> None:
        self.pending_tasks = [t for t in self.pending_tasks if t != task]
        self.save()

    def clear_tasks(self) -> None:
        self.pending_tasks = []
        self.save()


lena_state = LenaStateManager()