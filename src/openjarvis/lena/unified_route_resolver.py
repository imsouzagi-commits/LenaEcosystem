from __future__ import annotations

from openjarvis.lena.cognitive_orchestrator import CognitiveDecision


class UnifiedRouteResolver:
    @staticmethod
    def resolve(cognitive: CognitiveDecision) -> str:
        if cognitive.domain == "action" and cognitive.capability == "desktop":
            return "DESKTOP"

        if cognitive.domain == "action" and cognitive.capability == "file":
            return "FILE_OP"

        if cognitive.domain == "factual":
            return "WEB_SEARCH_BG"

        if cognitive.domain == "practical" and cognitive.capability == "local_search":
            return "LOCAL_SEARCH"

        return "CONVERSATIONAL_CORE"
