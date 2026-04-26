from __future__ import annotations

import re
import unicodedata


class WakewordResolver:
    def __init__(self):
        self.variants = {
            "lena", "lenda", "leana", "leina", "lela", "lina", "lenaah", "lenaa"
        }

    def _clean(self, text: str) -> str:
        text = text.lower().strip()
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"[^\w\s]", " ", text)
        return " ".join(text.split())

    def strip(self, text: str) -> str:
        words = self._clean(text).split()
        filtered = [w for w in words if w not in self.variants]
        return " ".join(filtered)