from __future__ import annotations

import re
from typing import Dict, List

from openjarvis.intelligence.action_schema import ActionBatch, ActionCommand
from openjarvis.intelligence.confidence_engine import ConfidenceEngine
from openjarvis.intelligence.spoken_entity_resolver import SpokenEntityResolver
from openjarvis.intelligence.wakeword_resolver import WakewordResolver


class OperationalParser:
    def __init__(self, installed_apps: Dict[str, str]):
        self.installed_apps = installed_apps
        self.entity_resolver = SpokenEntityResolver()
        self.wakeword_resolver = WakewordResolver()
        self.confidence_engine = ConfidenceEngine()

        self.intent_map = {
            "abre": ("open", "application"),
            "abrir": ("open", "application"),
            "abri": ("open", "application"),
            "abro": ("open", "application"),
            "abriga": ("open", "application"),
            "abrisa": ("open", "application"),
            "fecha": ("close", "application"),
            "fechar": ("close", "application"),
            "feche": ("close", "application"),
            "fecham": ("close", "application"),
            "fexa": ("close", "application"),
            "liga": ("on", "system"),
            "desliga": ("off", "system"),
            "aumenta": ("up", "system"),
            "abaixa": ("down", "system"),
        }

    def split_commands(self, text: str) -> List[str]:
        cleaned = self.wakeword_resolver.strip(text.lower())
        cleaned = re.sub(r"\s+", " ", cleaned)

        parts = re.split(r"\b(e|depois|then|and)\b|,", cleaned)

        return [
            p.strip()
            for p in parts
            if p and p.strip() and p.strip() not in {"e", "depois", "then", "and"}
        ]

    def detect_intent(self, text: str) -> tuple[str, str]:
        words = text.lower().split()

        for word in words:
            if word in self.intent_map:
                return self.intent_map[word]

        for word in words:
            if word.startswith("abr"):
                return "open", "application"

            if word.startswith("fec") or word.startswith("fech") or word.startswith("fex"):
                return "close", "application"

        return "unknown", "unknown"

    def parse(self, text: str) -> ActionBatch:
        commands = self.split_commands(text)
        batch = ActionBatch()

        for command_text in commands:
            intent, domain = self.detect_intent(command_text)

            resolved_target = ""
            resolved = False
            entity = None

            if domain == "application":
                entity = self.entity_resolver.resolve_entity(
                    self.wakeword_resolver.strip(command_text),
                    self.installed_apps,
                )

            if entity:
                resolved_target = entity
                resolved = True

            confidence = self.confidence_engine.score(
                intent=intent,
                domain=domain,
                target=resolved_target,
                resolved=resolved,
                raw_text=command_text,
            )

            batch.commands.append(
                ActionCommand(
                    raw_text=command_text,
                    normalized_text=command_text.strip(),
                    intent=intent,
                    domain=domain,
                    target=resolved_target,
                    confidence=confidence,
                    is_compound=len(commands) > 1,
                )
            )

        return batch