from __future__ import annotations


class LenaResponseRegimeResolver:
    @staticmethod
    def resolve(cognitive_domain: str, presence_mode: str) -> str:
        if cognitive_domain == "emotional":
            if presence_mode in {"mirror", "continuity", "invite"}:
                return presence_mode
            return "mirror"

        if cognitive_domain == "narrative":
            if presence_mode == "reflective_hold":
                return "contain"
            return "mirror"

        if cognitive_domain == "inquisitive":
            return "mirror"

        if cognitive_domain == "social":
            return "mirror"

        return "mirror"
