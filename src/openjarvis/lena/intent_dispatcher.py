from __future__ import annotations


class LenaIntentDispatcher:
    @staticmethod
    def dispatch(
        agent,
        route: str,
        user_text: str,
        cognitive=None,
        semantic_packet=None,
    ) -> str:
        lowered = user_text.lower().strip()

        if route == "DESKTOP":
            if not agent.desktop_controller:
                return "controle desktop indisponível."
            return agent.desktop_controller.execute(user_text)

        if route == "FILE_OP":
            if not agent.file_controller:
                return "controle de arquivos indisponível."
            return agent.file_controller.execute(user_text)

        if route == "WEB_OPEN":
            if not getattr(agent, "web_controller", None):
                return "web controller indisponível."
            return agent.web_controller.execute_open(user_text)

        if route == "WEB_SEARCH":
            if not getattr(agent, "web_controller", None):
                return "busca web indisponível."
            return agent.web_controller.execute_search(lowered, user_text)

        if route == "MEMORY":
            return agent.memory_engine.answer_memory_question(lowered)

        if route == "CONVERSATIONAL_CORE":
            return (
                agent.conversationer.respond(
                    agent,
                    user_text,
                    cognitive=cognitive,
                    semantic_packet=semantic_packet,
                )
                or "certo."
            )

        return agent.fallback_controller.execute(
            agent,
            lowered,
            user_text,
            route,
        )
