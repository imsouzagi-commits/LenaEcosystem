from __future__ import annotations

import difflib
import re
import unicodedata
from typing import Dict, List, Optional


def _ascii(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c)).lower()


class BrazilianPhoneticEngine:
    def __init__(self):
        self.noise_words = {
            "o", "a", "os", "as", "um", "uma",
            "de", "do", "da", "e", "pra", "para",
            "por", "favor", "me", "mim", "ai", "aí",
            "lena", "lina", "lenda", "leana", "leina", "lela", "mena"
        }

        self.action_words = {
            "abre", "abrir", "abri", "abro", "abriga", "abrisa", "abrico",
            "fecha", "fechar", "feche", "fexa", "fecham",
            "liga", "ligar", "desliga", "desligar",
            "aumenta", "abaixa"
        }

        self.phonetic_rules = [
            (r"^es", "s"),
            (r"^is", "s"),
            (r"ph", "f"),
            (r"th", "t"),
            (r"ou", "o"),
            (r"ei", "e"),
            (r"lh", "li"),
            (r"nh", "ni"),
            (r"tt", "t"),
            (r"pp", "p"),
            (r"ff", "f"),
            (r"([aeiou])r$", r"\1"),
            (r"([aeiou])m$", r"\1"),
            (r"([aeiou])n$", r"\1"),
        ]

    def clean_text(self, text: str) -> str:
        text = _ascii(text)
        text = re.sub(r"[^\w\s]", " ", text)
        return " ".join(text.split())

    def remove_noise(self, text: str) -> List[str]:
        words = self.clean_text(text).split()
        return [
            w for w in words
            if w not in self.noise_words and w not in self.action_words
        ]

    def apply_brazilian_rules(self, token: str) -> str:
        value = token

        for pattern, repl in self.phonetic_rules:
            value = re.sub(pattern, repl, value)

        return value

    def generate_candidates(self, text: str) -> List[str]:
        filtered_words = self.remove_noise(text)

        if not filtered_words:
            return []

        joined = " ".join(filtered_words)
        candidates = {joined}

        transformed_words = [
            self.apply_brazilian_rules(word)
            for word in filtered_words
        ]

        transformed_joined = " ".join(transformed_words)
        candidates.add(transformed_joined)

        for word in transformed_words:
            candidates.add(word)

        for word in filtered_words:
            candidates.add(word)

        return list(candidates)

    def resolve(self, spoken_text: str, candidates: Dict[str, str]) -> Optional[str]:
        generated = self.generate_candidates(spoken_text)

        if not generated:
            return None

        candidate_keys = list(candidates.keys())

        for possibility in generated:
            if possibility in candidates:
                return candidates[possibility]

        best_match = None
        best_score = 0.0

        for possibility in generated:
            matches = difflib.get_close_matches(possibility, candidate_keys, n=1, cutoff=0.40)
            if matches:
                match = matches[0]
                score = difflib.SequenceMatcher(None, possibility, match).ratio()

                if score > best_score:
                    best_score = score
                    best_match = match

        if best_match:
            return candidates[best_match]

        return None