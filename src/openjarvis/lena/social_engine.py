from __future__ import annotations


class LenaSocialEngine:
    @staticmethod
    def analyze(user_text: str) -> dict:
        lowered = user_text.lower().strip()

        emotional_markers = (
            "triste", "cansado", "desanimado", "sem vontade", "mal",
            "ansioso", "sozinho", "confuso", "perdido"
        )

        asks_company = any(x in lowered for x in (
            "vamos conversar",
            "fala comigo",
            "fica comigo",
            "quero conversar",
        ))

        asks_opinion = any(x in lowered for x in (
            "o que você acha",
            "o que você percebe",
            "como você me vê",
        ))

        reflective = any(x in lowered for x in (
            "você tá me entendendo",
            "isso é estranho",
            "me responde sinceramente",
            "se você fosse humana",
        ))

        return {
            "emotional": any(x in lowered for x in emotional_markers),
            "asks_company": asks_company,
            "asks_opinion": asks_opinion or reflective,
            "open_user": len(lowered.split()) >= 4,
            "is_question": lowered.endswith("?"),
        }
