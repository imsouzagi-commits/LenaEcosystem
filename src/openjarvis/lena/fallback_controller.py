from __future__ import annotations

from openjarvis.lena.boot_logger import LenaBootLogger


class LenaFallbackController:
    @staticmethod
    def execute(agent, lowered: str, user_text: str, route: str = "UNKNOWN") -> str:
        try:
            smart = agent.conversationer.respond(agent, user_text)
            if smart and smart.strip():
                return smart
        except Exception as exc:
            LenaBootLogger.write(f"fallback conversationer failed: {exc}")

        LenaBootLogger.write(f"hard fallback activated on route={route}")
        return "te ouvi."
