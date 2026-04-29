from __future__ import annotations

import random
import re

from openjarvis.agent.lena_social_engine import SocialSignal


_AI_RESIDUE_REGEX = re.compile(
    r"(como inteligência artificial[, ]*|como uma ia[, ]*|como assistente virtual[, ]*|"
    r"estou aqui para ajudar[, ]*|fico feliz em ajudar[, ]*|posso te ajudar com isso[, ]*|"
    r"claro[, ]*|certamente[, ]*)",
    flags=re.IGNORECASE,
)

_WORD_VARIATIONS = (
    (" você ", (" você ", " tu ")),
    (" está ", (" tá ", " está ")),
    (" estou ", (" tô ", " estou ")),
    (" para ", (" pra ", " para ")),
)

_EXCESSIVE_POLITENESS = (
    ("entendo perfeitamente", "entendo"),
    ("compreendo perfeitamente", "entendo"),
    ("isso é uma excelente pergunta", "boa pergunta"),
    ("essa é uma ótima pergunta", "boa"),
    ("eu acredito que", "acho que"),
    ("na minha opinião", "acho"),
)

_HESITATIONS = ("hm...", "hmm...", "é...", "olha...")
_WARM_PREFIX = ("tô aqui.", "eu tô contigo.", "sim...")
_DENSE_PREFIX = ("sinceramente,", "te lendo aqui,", "olhando isso,")
_REPEAT_SUFFIX = (" ...", ".", " enfim.", " né.")


class LenaResponseMutator:
    def __init__(self) -> None:
        self.last_outputs: list[str] = []

    def mutate(self, text: str, social: SocialSignal) -> str:
        if not text:
            return text

        mutated = " ".join(text.strip().split())
        lowered = mutated.lower()

        if "como " in lowered or "ajudar" in lowered:
            mutated = _AI_RESIDUE_REGEX.sub("", mutated).strip()
            lowered = mutated.lower()

        for old, new in _EXCESSIVE_POLITENESS:
            if old in lowered:
                mutated = mutated.replace(old, new).replace(old.title(), new.capitalize())
                lowered = mutated.lower()

        mode = social.social_mode

        if mode == "emotional":
            mutated = self._soften(mutated)
        elif mode == "attachment":
            mutated = self._warmify(mutated)
        elif mode == "introspective":
            mutated = self._densify(mutated)
        elif mode == "casual_light":
            mutated = self._lightify(mutated)

        if (
            social.user_neediness >= 0.24
            or social.validation_need >= 0.20
            or social.abandonment_fear >= 0.30
            or social.existential_depth >= 0.30
        ):
            mutated = self._apply_hesitation(mutated)

        if social.intimacy_level >= 0.45:
            mutated = self._apply_shortening(mutated)

        mutated = self._apply_variation_fast(mutated)
        mutated = self._avoid_repetition(mutated)

        self.last_outputs.append(mutated)
        if len(self.last_outputs) > 20:
            del self.last_outputs[:-20]

        return mutated.strip()

    def _apply_hesitation(self, text: str) -> str:
        if text.startswith(_HESITATIONS):
            return text
        return f"{random.choice(_HESITATIONS)} {text}"

    def _apply_shortening(self, text: str) -> str:
        dot_positions = [i for i, char in enumerate(text) if char == "."]
        if len(dot_positions) < 2:
            return text
        return text[: dot_positions[1] + 1].strip()

    def _apply_variation_fast(self, text: str) -> str:
        padded = f" {text} "
        lowered = padded.lower()

        for needle, variants in _WORD_VARIATIONS:
            if needle in lowered:
                replacement = random.choice(variants)
                padded = padded.replace(needle, replacement, 1)
                lowered = padded.lower()

        return padded.strip()

    def _avoid_repetition(self, text: str) -> str:
        if text in self.last_outputs[-5:]:
            return text + random.choice(_REPEAT_SUFFIX)
        return text

    def _soften(self, text: str) -> str:
        if len(text) < 18:
            return text
        if text.startswith("Você"):
            return text.replace("Você", "Poxa, você", 1)
        return text

    def _warmify(self, text: str) -> str:
        if text.startswith(_HESITATIONS):
            return text
        return f"{random.choice(_WARM_PREFIX)} {text}"

    def _densify(self, text: str) -> str:
        if "acho" in text.lower():
            return text
        return f"{random.choice(_DENSE_PREFIX)} {text}"

    def _lightify(self, text: str) -> str:
        return text.replace("você", "tu").replace("Você", "Tu")