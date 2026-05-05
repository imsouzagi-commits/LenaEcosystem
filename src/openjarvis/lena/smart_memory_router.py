from __future__ import annotations


class LenaSmartMemoryRouter:
    @classmethod
    def try_answer(cls, lowered: str, memory_engine) -> str | None:
        profile = memory_engine.user_profile

        if "qual meu nome" in lowered:
            if profile.name:
                return f"teu nome é {profile.name}."

        if "onde eu moro" in lowered:
            if profile.location:
                return f"tu mora em {profile.location}."

        if "o que eu estudo" in lowered or "qual curso eu faço" in lowered:
            if profile.study:
                return f"tu estuda {profile.study}."

        if "qual é meu projeto principal" in lowered or "meu projeto principal" in lowered:
            if profile.main_project:
                return f"teu projeto principal é {profile.main_project}."

        if "o que além de tecnologia eu faço" in lowered:
            if profile.music_focus:
                return f"além de tecnologia tu também tá evoluindo em {profile.music_focus}."

        if "o que você acha que eu busco" in lowered:
            return "tu busca evolução com estrutura, não crescimento bagunçado."

        if "quais áreas eu tento equilibrar" in lowered:
            return "tu tenta equilibrar carreira, estudos, música e desenvolvimento pessoal."

        return None
