# src/openjarvis/intelligence/voice_command_normalizer.py

from __future__ import annotations

import re


class VoiceCommandNormalizer:
    def __init__(self):
        self.wakeword_patterns = [
            r"\blena\b",
            r"\blenda\b",
            r"\bleana\b",
            r"\bleina\b",
            r"\blenna\b",
            r"\blê na\b",
            r"\ble na\b",
            r"\blenaa\b",
        ]

        self.verb_replacements = {
            r"\babriço\b": "abre",
            r"\babris\b": "abre",
            r"\babripa\b": "abre",
            r"\babrifa\b": "abre",
            r"\babrisa\b": "abre",
            r"\babresa\b": "abre",
            r"\babriza\b": "abre",
            r"\babril\b": "abre",

            r"\bfechaa\b": "fecha",
            r"\bfeichar\b": "fecha",
            r"\bficha\b": "fecha",
            r"\bfeixa\b": "fecha",
            r"\bfeixo\b": "fecha",
            r"\bfeisha\b": "fecha",
            r"\bfexa\b": "fecha",

            r"\bligaa\b": "liga",
            r"\bdisliga\b": "desliga",

            r"\baumentaa\b": "aumenta",
            r"\babaixaa\b": "abaixa",
        
            r"\babresafari\b": "abre safari",
            r"\babrisafari\b": "abre safari",
            r"\babrosafari\b": "abre safari",
            r"\babresafario\b": "abre safari",
            r"\babresafária\b": "abre safari",

            r"\babrespotify\b": "abre spotify",
            r"\babrispotify\b": "abre spotify",
            r"\babrospotify\b": "abre spotify",
            r"\babrespotifai\b": "abre spotify",
            r"\babrispotifai\b": "abre spotify",

            r"\bfechasafari\b": "fecha safari",
            r"\bfeichesafari\b": "fecha safari",
            r"\bfechasafario\b": "fecha safari",

            r"\bfechaspotify\b": "fecha spotify",
            r"\bfeichaspotify\b": "fecha spotify",
            r"\bfechaspotifai\b": "fecha spotify",
        }
        

        self.noise_words = [
            "o", "a", "os", "as", "um", "uma",
            "por favor", "pra mim", "para mim",
            "rapidinho", "ai", "aí"
        ]

    def normalize(self, text: str) -> str:
        q = text.lower().strip()

        for pattern in self.wakeword_patterns:
            q = re.sub(pattern, "", q)

        q = re.sub(r"[\,\.\!\?]", " ", q)

        for wrong, correct in self.verb_replacements.items():
            q = re.sub(wrong, correct, q)

        for noise in self.noise_words:
            q = re.sub(rf"\b{re.escape(noise)}\b", "", q)

        q = " ".join(q.split())
        return q