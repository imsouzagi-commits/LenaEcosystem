from __future__ import annotations

import difflib
import re
import unicodedata
from typing import Dict, List, Tuple

from openjarvis.intelligence.uo_action_schema import UOBatch, UOCommand
from openjarvis.intelligence.uo_target_registry import UOTargetRegistry
from openjarvis.intelligence.brazilian_phonetic_engine import BrazilianPhoneticEngine


def _ascii(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c)).lower()


class UOSemanticInterpreter:
    def __init__(self, installed_apps: Dict[str, str]):
        self.registry = UOTargetRegistry(installed_apps)
        self.phonetic_engine = BrazilianPhoneticEngine()

        self.noise_words = {
            "lena", "lina", "lenda", "leana", "leina", "lela", "mena",
            "o", "a", "os", "as", "um", "uma",
            "de", "do", "da", "pra", "para", "por", "favor",
            "me", "mim", "ai", "aí"
        }

        self.intent_aliases = {
            "open": ["abre", "abrir", "abri", "abro", "abriga", "abrisa", "abrico", "abdi", "abd"],
            "close": ["fecha", "fechar", "feche", "fexa", "fecham", "fechao", "fech"],
            "on": ["liga", "ligar", "ative", "ativa"],
            "off": ["desliga", "desligar", "desative", "desativa"],
            "up": ["aumenta", "aumentar", "sobe", "sube"],
            "down": ["abaixa", "abaixar", "diminu", "desce"],
        }

        self.intent_prefixes = {
            "open": ["abr", "abd"],
            "close": ["fec", "fech", "fex"],
            "on": ["lig"],
            "off": ["desl"],
            "up": ["aum", "sob"],
            "down": ["aba", "dim", "des"],
        }

    def _clean(self, text: str) -> str:
        text = _ascii(text)
        text = re.sub(r"[^\w\s]", " ", text)
        return " ".join(text.split())

    def _split_commands(self, text: str) -> List[str]:
        cleaned = self._clean(text)
        parts = re.split(r"\b(e|depois|then|and)\b|,", cleaned)

        return [
            p.strip()
            for p in parts
            if p and p.strip() and p.strip() not in {"e", "depois", "then", "and"}
        ]

    def _detect_single_word_intent(self, word: str) -> str | None:
        for intent, aliases in self.intent_aliases.items():
            for alias in aliases:
                ratio = difflib.SequenceMatcher(None, word, alias).ratio()
                if ratio >= 0.72:
                    return intent

        for intent, prefixes in self.intent_prefixes.items():
            for prefix in prefixes:
                if word.startswith(prefix):
                    return intent

        return None

    def _extract_glued_intent_target(self, word: str) -> Tuple[str | None, List[str]]:
        for intent, prefixes in self.intent_prefixes.items():
            for prefix in prefixes:
                if word.startswith(prefix) and len(word) > len(prefix):
                    remainder = word[len(prefix):].strip()
                    if remainder:
                        return intent, [remainder]

        return None, [word]

    def _detect_intent(self, words: List[str]) -> tuple[str, List[str]]:
        for idx, word in enumerate(words):
            if len(word) >= 6:
                glued_intent, glued_remaining = self._extract_glued_intent_target(word)
                if glued_intent:
                    remaining = glued_remaining + words[idx + 1:]
                    return glued_intent, remaining

            direct = self._detect_single_word_intent(word)
            if direct:
                return direct, words[idx + 1:]

        return "unknown", words

    def _resolve_target(self, words: List[str]) -> tuple[str, str]:
        filtered = [w for w in words if w not in self.noise_words]

        if not filtered:
            return "", "unknown"

        spoken = " ".join(filtered)
        all_targets = self.registry.all_targets()

        resolved = self.phonetic_engine.resolve(spoken, all_targets)

        if not resolved:
            return "", "unknown"

        if resolved in {"wifi", "bluetooth", "volume", "brilho"}:
            return resolved, "system"

        return resolved, "application"

    def interpret(self, text: str) -> UOBatch:
        batch = UOBatch()
        commands = self._split_commands(text)

        last_intent = "unknown"
        last_domain = "unknown"

        for raw_command in commands:
            words = self._clean(raw_command).split()

            if not words:
                continue

            intent, remaining = self._detect_intent(words)
            target, domain = self._resolve_target(remaining)

            if intent == "unknown" and target:
                intent = last_intent
                domain = last_domain

            if intent != "unknown":
                last_intent = intent

            if domain != "unknown":
                last_domain = domain

            confidence = 0.0
            if intent != "unknown":
                confidence += 0.5
            if target:
                confidence += 0.5

            batch.commands.append(
                UOCommand(
                    raw_text=raw_command,
                    intent=intent,
                    domain=domain,
                    target=target,
                    confidence=confidence,
                )
            )

        return batch