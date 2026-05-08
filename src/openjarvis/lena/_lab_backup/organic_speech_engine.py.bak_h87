from __future__ import annotations

import random
import re

from openjarvis.lena.semantic_response_bank import LenaSemanticResponseBank
from openjarvis.lena.intention_memory_engine import LenaIntentionMemoryEngine


class LenaOrganicSpeechEngine:
    @staticmethod
    def _clean(text: str | None) -> str:
        return " ".join((text or "").strip().split())

    @classmethod
    def _intent_of(cls, text: str | None) -> str:
        tx = (text or "").lower()

        groups = {
            "unity_loss": ["encontr", "inteiro", "reun", "desencontr", "eixo", "encaixa", "lugar"],
            "no_progress": ["mudando", "deslocamento", "parada", "mesmo trilho", "tempo passa", "mesmo ponto", "anda"],
            "unresolved": ["encerr", "fecha", "aberta", "resolução", "concluir", "pendurado"],
            "drained": ["desgaste", "recompõe", "recupera", "cansaço", "margem", "drenad"],
            "clarity": ["entender", "estruturar", "organizar", "linha compreensível"],
            "noise": ["aquieta", "atravessando", "linha contínua", "ruído", "embaralh"],
        }

        for tag, roots in groups.items():
            if any(root in tx for root in roots):
                return tag

        return tx[:24]

    @classmethod
    def _same_semantic_family(cls, a: str | None, b: str | None) -> bool:
        if not a or not b:
            return False
        return cls._intent_of(a) == cls._intent_of(b)

    @classmethod
    def _is_recently_used(cls, memory, candidate: str) -> bool:
        for text in memory.recent_semantic_responses(memory.social_state.current_topic or "uncertainty"):
            if cls._same_semantic_family(candidate, text):
                return True
        return False

    @classmethod
    def _pick_fresh(cls, memory, pool: list[str]) -> str:
        recent_fragments = set(memory.recent_semantic_fragments())
        fresh = [
            p for p in pool
            if not cls._is_recently_used(memory, p)
            and p.strip().lower() not in recent_fragments
        ]
        choice = random.choice(fresh) if fresh else random.choice(pool)
        memory.remember_semantic_fragment(choice)
        return choice

    @classmethod
    def _join_unique(cls, fragments: list[str]) -> str:
        chosen = []
        for fragment in fragments:
            fragment = cls._clean(fragment)
            if not fragment:
                continue
            if any(cls._same_semantic_family(fragment, x) for x in chosen):
                continue
            chosen.append(fragment)
        return " ".join(chosen).strip()

    @classmethod
    def _anchor_fragment(cls, memory, topic: str) -> str:
        return cls._pick_fresh(memory, LenaSemanticResponseBank.role_anchor(topic))

    @classmethod
    def _support_fragment(cls, memory, topic: str, stance: str) -> str | None:
        if stance not in {"pattern_link", "locate", "compress"}:
            return None
        return cls._pick_fresh(memory, LenaSemanticResponseBank.role_subjective(topic))

    @classmethod
    def _continuity_fragment(cls, memory, topic: str, stance: str) -> str | None:
        if stance not in {"pattern_link", "locate", "compress"}:
            return None
        pool = LenaSemanticResponseBank.role_temporal(topic)
        return cls._pick_fresh(memory, pool)

    @classmethod
    def _probe_cognitive_fragment(cls, memory, topic: str) -> str | None:
        return cls._pick_fresh(memory, LenaSemanticResponseBank.role_cognitive(topic))

    @classmethod
    def _probe_fragment(cls, memory, topic: str) -> str | None:
        if random.random() < 0.40:
            return cls._pick_fresh(memory, LenaSemanticResponseBank.role_probe(topic))
        return None

    @classmethod
    def _surface_clean(cls, text: str) -> str:
        tx = text

        tx = re.sub(r'\s+,', ',', tx)
        tx = re.sub(r'\s+\.', '.', tx)
        tx = re.sub(r'\s+', ' ', tx)

        tx = tx.replace("..", ".")
        tx = tx.replace(",.", ".")
        tx = tx.replace(". Porque", " porque")
        tx = tx.replace(". porque", " porque")
        tx = tx.replace("vai te deixa", "vai te deixando")

        return tx.strip()



    @classmethod
    def _build_discursive_line(
        cls,
        memory,
        anchor: str,
        subjective: str | None,
        temporal: str | None,
        cognitive: str | None,
        secondary_fragment: str | None = None,
    ) -> str:
        anchor = cls._clean(anchor).rstrip(".")
        subjective = cls._clean(subjective).rstrip(".") if subjective else None
        temporal = cls._clean(temporal).rstrip(".") if temporal else None
        cognitive = cls._clean(cognitive).rstrip(".") if cognitive else None
        secondary_fragment = cls._clean(secondary_fragment).rstrip(".") if secondary_fragment else None

        variants = [anchor + "."]

        if subjective and cognitive:
            variants.append(f"{anchor}, {subjective}, porque {cognitive}.")
            variants.append(f"{anchor}, e isso vai gerando {subjective}, porque {cognitive}.")
            variants.append(f"{anchor}. {subjective.capitalize()} porque {cognitive}.")

        if temporal and cognitive:
            variants.append(f"{anchor}, {temporal}, porque {cognitive}.")
            variants.append(f"{anchor}. {temporal.capitalize()}, já que {cognitive}.")
            variants.append(f"{anchor}, e com o tempo {temporal}, porque {cognitive}.")

        if subjective and temporal:
            variants.append(f"{anchor}, {subjective}, e {temporal}.")
            variants.append(f"{anchor}. {subjective.capitalize()}. Com o tempo {temporal}.")

        if subjective and temporal and cognitive:
            variants.append(f"{anchor}, {subjective}, e {temporal}, porque {cognitive}.")
            variants.append(f"{anchor}. {subjective.capitalize()}. {temporal.capitalize()} porque {cognitive}.")

        if secondary_fragment:
            variants.append(f"{anchor}, enquanto {secondary_fragment}.")
            if subjective:
                variants.append(f"{anchor}, {subjective}, enquanto {secondary_fragment}.")
            if cognitive:
                variants.append(f"{anchor}, porque {cognitive}, enquanto {secondary_fragment}.")
            if subjective and cognitive:
                variants.append(f"{anchor}, {subjective}, porque {cognitive}, enquanto {secondary_fragment}.")

        weighted = variants
        chosen = random.choice(weighted)
        return cls._surface_clean(chosen)

    @classmethod
    def _build_response(
        cls,
        memory,
        primary_topic: str,
        stance: str,
        secondary_topic: str | None = None,
        latent_topic: str | None = None,
    ) -> list[str]:
        topics = [x for x in [primary_topic, secondary_topic, latent_topic] if x]

        anchor_topic = primary_topic
        subjective_topic = secondary_topic or primary_topic
        temporal_topic = latent_topic or secondary_topic or primary_topic
        cognitive_topic = secondary_topic or latent_topic or primary_topic

        anchor = cls._anchor_fragment(memory, anchor_topic)
        subjective = cls._support_fragment(memory, subjective_topic, stance)
        temporal = cls._continuity_fragment(memory, temporal_topic, stance)
        cognitive = cls._probe_cognitive_fragment(memory, cognitive_topic)

        secondary_fragment = None
        if len(topics) >= 2:
            secondary_pool = [
                cls._anchor_fragment(memory, secondary_topic or primary_topic),
                cls._support_fragment(memory, secondary_topic or primary_topic, stance),
                cls._continuity_fragment(memory, secondary_topic or primary_topic, stance),
                cls._probe_cognitive_fragment(memory, secondary_topic or primary_topic),
            ]
            secondary_pool = [x for x in secondary_pool if x]
            secondary_fragment = random.choice(secondary_pool) if secondary_pool else None

        mainline = cls._build_discursive_line(
            memory,
            anchor,
            subjective,
            temporal,
            cognitive,
            secondary_fragment,
        )

        fragments = [mainline]

        if len(topics) >= 2:
            extra_secondary_pool = [
                cls._anchor_fragment(memory, secondary_topic or primary_topic),
                cls._support_fragment(memory, secondary_topic or primary_topic, stance),
                cls._continuity_fragment(memory, secondary_topic or primary_topic, stance),
                cls._probe_cognitive_fragment(memory, secondary_topic or primary_topic),
            ]
            extra_secondary_pool = [x for x in extra_secondary_pool if x]
            if extra_secondary_pool:
                fragments.append(random.choice(extra_secondary_pool))

        if latent_topic:
            latent_pool = [
                cls._anchor_fragment(memory, latent_topic),
                cls._support_fragment(memory, latent_topic, stance),
                cls._continuity_fragment(memory, latent_topic, stance),
                cls._probe_cognitive_fragment(memory, latent_topic),
            ]
            latent_pool = [x for x in latent_pool if x]
            if latent_pool:
                fragments.append(random.choice(latent_pool))

        if random.random() < 0.55:
            probe = cls._probe_fragment(memory, cognitive_topic)
            if probe:
                fragments.append(probe)

        return fragments

    @classmethod
    def synthesize(
        cls,
        memory,
        user_text: str,
        topic: str,
        mode: str,
        stance: str = "observe",
        secondary_topic: str | None = None,
        latent_topic: str | None = None,
    ) -> str:
        fragments = cls._build_response(
            memory,
            topic,
            stance,
            secondary_topic=secondary_topic,
            latent_topic=latent_topic,
        )
        if not fragments:
            text = cls._anchor_fragment(memory, topic)
        else:
            mainline = fragments[0]
            probe_line = None
            if len(fragments) > 1 and random.random() < 0.45:
                probe_line = fragments[-1]

            text = mainline
            if probe_line and probe_line != mainline:
                text = f"{mainline} {probe_line}"

        memory.remember_semantic_response(topic, text)

        if mode == "invite":
            LenaIntentionMemoryEngine.capture(memory, "exploration", topic, text)
        elif mode == "contain":
            LenaIntentionMemoryEngine.capture(memory, "contain", topic, text)
        elif mode == "continuity":
            LenaIntentionMemoryEngine.capture(memory, "continuity_hold", topic, text)

        return LenaSemanticResponseBank.soften(memory, text)

    @classmethod
    def synthesize_greeting(cls, memory, topic: str) -> str:
        return cls._pick_fresh(memory, LenaSemanticResponseBank.greeting_fragments(topic))
