from __future__ import annotations

from openjarvis.lena.boot_logger import LenaBootLogger


class LenaIntentDispatcher:
    @staticmethod
    def dispatch(agent, route: str, user_text: str, cognitive=None) -> str:
        lowered = user_text.lower().strip()

        try:
            if route == "DESKTOP":
                return agent.desktop_controller.execute(user_text)

            if route == "FILE_OP":
                return agent.file_controller.execute(user_text)

            if route == "WEB_OPEN":
                return agent.web_controller.execute_open(user_text)

            if route == "WEB_SEARCH":
                return agent.web_controller.execute_search(lowered, user_text)

            if route == "MEMORY":
                return agent.memory_engine.answer_memory_question(lowered)

            if route == "CONVERSATIONAL_CORE":
                return agent.conversationer.respond(agent, user_text, cognitive=cognitive) or "certo."

            return agent.fallback_controller.execute(agent, lowered, user_text, route)

        except Exception as exc:
            LenaBootLogger.write(f"dispatcher route {route} failed: {exc}")
            return f"DEBUG_DISPATCH_ERROR: {type(exc).__name__}: {exc}"
