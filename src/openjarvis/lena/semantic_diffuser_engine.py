from __future__ import annotations


class LenaSemanticDiffuserEngine:
    FAMILY_RULES = {
        "open_loop": (
            "a gente ainda não encerrou",
            "isso ficou aberto",
            "continua suspenso",
            "ponto que ficou aberto",
            "ainda tá no meio dessa leitura",
        ),
        "pattern_notice": (
            "eu tô percebendo esse padrão",
            "isso vem aparecendo com frequência",
            "ganhando cara de padrão",
            "ficando visível na recorrência",
            "não soa mais como algo pontual",
        ),
        "organization_failure": (
            "continua difícil organizar",
            "não tá encaixando direito",
            "falta de encaixe",
            "pensamento sem fechamento",
            "não conseguir organizar",
        ),
        "deepening_state": (
            "deixando de ser episódio isolado",
            "adquirindo constância cognitiva",
            "já começa a parecer um estado",
            "ruído mental contínuo",
        ),
    }

    @classmethod
    def _family(cls, text: str) -> str:
        lowered = text.lower()
        for family, markers in cls.FAMILY_RULES.items():
            if any(marker in lowered for marker in markers):
                return family
        return lowered

    @classmethod
    def diffuse(cls, memory, fragments: list[str]) -> list[str]:
        accepted: list[str] = []
        seen_families: set[str] = set()

        recent = " ".join(
            memory.recent_semantic_responses(memory.social_state.current_topic or "uncertainty")
        ).lower()

        for fragment in fragments:
            cleaned = fragment.strip()
            if not cleaned:
                continue

            family = cls._family(cleaned)

            if family in seen_families:
                continue

            if cleaned.lower() in recent:
                continue

            seen_families.add(family)
            accepted.append(cleaned)

        return accepted
