from __future__ import annotations

import re
from typing import Optional

from openjarvis.lena.action_center import ActionCenter


class CommandCenter:
    def __init__(self, action_center: ActionCenter):
        self.action_center = action_center

    def normalize(self, query: str) -> str:
        q = query.lower().strip()
        q = re.sub(r"[^\w\s]", "", q)

        replacements = {
            "ligar": "liga",
            "ligue": "liga",
            "desligar": "desliga",
            "desligue": "desliga",
            "abrir": "abre",
            "abra": "abre",
            "fechar": "fecha",
            "feche": "fecha",
            "aumentar": "aumenta",
            "aumente": "aumenta",
            "abaixar": "abaixa",
            "abaixe": "abaixa",
            "som": "volume",
            "áudio": "volume",
            "audio": "volume",
            "internet": "wifi",
            "wi fi": "wifi",
            "navegador": "safari",
        }

        for old, new in replacements.items():
            q = q.replace(old, new)

        return " ".join(q.split())

    def detect_local(self, query: str) -> bool:
        local_words = [
            "abre",
            "fecha",
            "liga",
            "desliga",
            "aumenta",
            "abaixa",
            "wifi",
            "volume",
            "brilho",
            "spotify",
            "safari",
            "finder",
            "whatsapp",
            "oi lena",
            "bom dia lena",
            "boa tarde lena",
            "boa noite lena",
        ]
        return any(word in query.lower() for word in local_words)

    def execute(self, query: str) -> Optional[str]:
        q = self.normalize(query)

        if q == "desliga wifi":
            return self.action_center.wifi_off()

        if q == "liga wifi":
            return self.action_center.wifi_on()

        if q == "aumenta volume":
            return self.action_center.volume_up()

        if q == "abaixa volume":
            return self.action_center.volume_down()

        if q == "aumenta brilho":
            return self.action_center.brightness_up()

        if q == "abaixa brilho":
            return self.action_center.brightness_down()

        if q in {"oi lena", "olá lena", "ola lena"}:
            return "Oi Thiago, estou aqui."

        if q == "bom dia lena":
            return "Bom dia Thiago."

        if q == "boa tarde lena":
            return "Boa tarde Thiago."

        if q == "boa noite lena":
            return "Boa noite Thiago."

        if q.startswith("abre "):
            target = q.replace("abre ", "").strip()
            return self.action_center.open_app(target)

        if q.startswith("fecha "):
            target = q.replace("fecha ", "").strip()
            return self.action_center.close_app(target)

        return None