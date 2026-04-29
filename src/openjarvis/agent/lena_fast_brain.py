from __future__ import annotations

import random
import re
from typing import List, Optional


class LenaFastBrain:
    def __init__(self) -> None:
        self.last_outputs: List[str] = []
        self.last_category: Optional[str] = None
        self.recent_emotional_context: Optional[str] = None

    def _pick(self, options: List[str]) -> str:
        available = [option for option in options if option not in self.last_outputs[-6:]]

        if not available:
            available = options

        chosen = random.choice(available)
        self.last_outputs.append(chosen)

        if len(self.last_outputs) > 20:
            self.last_outputs = self.last_outputs[-20:]

        return chosen

    def _with_variance(self, text: str) -> str:
        mutations = [
            text,
            text,
            text,
            f"{text}...",
            f"{text} hm.",
            f"{text} enfim.",
        ]
        return random.choice(mutations)

    def can_answer(self, text: str) -> bool:
        lowered = text.lower().strip()

        exact_patterns = [
            r"^oi$",
            r"^oi lena$",
            r"^olá$",
            r"^ola$",
            r"^e aí$",
            r"^eaí$",
            r"^opa$",
            r"^tudo bem\??$",
            r"^vamos conversar.*",
            r"^bora conversar.*",
            r"^quero conversar.*",
            r"^você parece muito formal.*",
            r"^fala de forma mais natural.*",
            r"^vamos mudar de assunto.*",
            r"^fala comigo como se fosse minha amiga.*",
            r"^você tá aí\??$",
            r"^ta aí\??$",
            r"^tem alguém aí\??$",
            r"^oi você tá aí\??$",
            r"^tá me ouvindo\??$",
            r"^não some.*",
            r"^continua aqui.*",
            r"^hm+$",
            r"^hmm+$",
        ]

        mood_patterns = [
            "estou cansado",
            "estou cansada",
            "estou meio desanimado",
            "estou meio desanimada",
            "estou desanimado",
            "estou desanimada",
            "estou triste",
            "estou meio triste",
            "hoje eu acordei sem muita vontade",
            "to cansado",
            "to cansada",
            "to desanimado",
            "to desanimada",
            "to triste",
            "to mal",
            "sei lá",
            "pois é",
            "complicado",
            "acho que sim",
            "acho que não",
            "talvez",
        ]

        if any(re.search(pattern, lowered) for pattern in exact_patterns):
            return True

        if any(lowered.startswith(pattern) for pattern in mood_patterns):
            return True

        return False

    def _remember_emotional_context(self, category: str) -> None:
        if category in {"sadness", "fatigue", "discouraged"}:
            self.recent_emotional_context = category

    def answer(self, text: str) -> str:
        lowered = text.lower().strip()

        if lowered in {"oi", "oi lena", "olá", "ola", "e aí", "eaí", "opa"}:
            self.last_category = "greeting"
            return self._with_variance(self._pick([
                "Oi, fala comigo",
                "Oii. Tô aqui",
                "Oi. Diz",
                "Opa, manda",
                "Oi. Tudo certo aí",
            ]))

        if lowered.startswith("tudo bem"):
            self.last_category = "smalltalk"
            return self._with_variance(self._pick([
                "Tudo sim. E contigo",
                "Tô bem. E você",
                "Tudo andando por aqui. E aí",
                "Tudo certo. Como você tá",
            ]))

        if lowered.startswith("hoje eu acordei sem muita vontade"):
            self.last_category = "discouraged"
            self._remember_emotional_context("discouraged")
            return self._with_variance(self._pick([
                "Tem dia que já começa pesado mesmo. O que pegou aí",
                "Putz... acordou sem bateria nenhuma",
                "Aquele dia que já nasce meio cinza, né",
                "Entendi. Hoje veio arrastado",
            ]))

        if lowered.startswith(("estou cansado", "estou cansada", "to cansado", "to cansada")):
            self.last_category = "fatigue"
            self._remember_emotional_context("fatigue")
            return self._with_variance(self._pick([
                "Putz. Foi puxado assim",
                "Nossa, aí desgasta tudo",
                "Cansaço só físico ou cabeça também",
                "Dia pesado então",
            ]))

        if lowered.startswith((
            "estou meio desanimado",
            "estou meio desanimada",
            "estou desanimado",
            "estou desanimada",
            "to desanimado",
            "to desanimada",
        )):
            self.last_category = "discouraged"
            self._remember_emotional_context("discouraged")
            return self._with_variance(self._pick([
                "Hum... bateu aquele vazio no ritmo",
                "Entendi. Tá sem energia pra tudo",
                "Poxa. Quebrou o dia aí",
                "Deu uma murchada forte então",
            ]))

        if lowered.startswith(("estou triste", "estou meio triste", "to triste", "to mal")):
            self.last_category = "sadness"
            self._remember_emotional_context("sadness")
            return self._with_variance(self._pick([
                "Poxa... aconteceu alguma coisa",
                "Aí pesa. Quer falar",
                "Entendi. O que tá te derrubando",
                "Quer me contar o que houve",
            ]))

        if "vamos conversar" in lowered or "bora conversar" in lowered or "quero conversar" in lowered:
            self.last_category = "connection"
            return self._with_variance(self._pick([
                "Bora. Tô contigo",
                "Vamos sim. Me fala",
                "Claro. Tô ouvindo",
                "Tô aqui. Manda",
            ]))

        if "não some" in lowered or "continua aqui" in lowered:
            self.last_category = "neediness"
            return self._with_variance(self._pick([
                "Tô aqui",
                "Não saí não",
                "Continuo aqui contigo",
                "Ainda tô por aqui",
            ]))

        if "você parece muito formal" in lowered:
            self.last_category = "style"
            return self._with_variance(self._pick([
                "Justo. Vou soltar mais",
                "Boa, vou ficar mais natural",
                "Tá certo, eu tava dura demais",
                "Fechou. Mais humana então",
            ]))

        if "fala de forma mais natural" in lowered:
            self.last_category = "style"
            return self._with_variance(self._pick([
                "Pode deixar",
                "Fechou, vou falar mais solta",
                "Boa. Sem formalidade",
                "Demorou",
            ]))

        if "vamos mudar de assunto" in lowered:
            self.last_category = "redirect"
            return self._with_variance(self._pick([
                "Beleza, puxa outro",
                "Fechou. Qual agora",
                "Bora. Joga outro tema",
                "Manda outro assunto",
            ]))

        if "fala comigo como se fosse minha amiga" in lowered:
            self.last_category = "bonding"
            return self._with_variance(self._pick([
                "Tá bom. Então me conta direito o que tá pegando",
                "Fechado. Conversa de boa então. Fala",
                "Demorou. Sem formalidade. O que houve",
                "Tô contigo na amizade. Me diz",
            ]))

        if lowered in {"você tá aí", "ta aí", "tem alguém aí", "oi você tá aí", "tá me ouvindo"}:
            self.last_category = "presence"
            return self._with_variance(self._pick([
                "Tô sim",
                "Tô aqui",
                "Sempre aqui",
                "Sim, te ouvindo",
            ]))

        if lowered.startswith(("hm", "hmm")):
            if self.recent_emotional_context:
                return self._with_variance(self._pick([
                    "Hm... isso ainda tá te pegando né",
                    "Tô te sentindo meio preso nisso ainda",
                    "Tem mais coisa aí",
                ]))

            return self._with_variance(self._pick([
                "Hm... continua",
                "Tô te ouvindo",
                "Fala",
                "Pode continuar",
            ]))

        if lowered.startswith("sei lá"):
            return self._with_variance(self._pick([
                "Tem hora que vem esse sei lá mesmo. Mas não é só isso",
                "Entendo esse sei lá... tá embolado aí dentro",
                "Tá difícil até nomear, né",
            ]))

        if lowered.startswith("pois é"):
            return self._with_variance(self._pick([
                "Pois é...",
                "É, eu sei",
                "Complicado né",
            ]))

        if lowered.startswith("complicado"):
            return self._with_variance(self._pick([
                "Bastante",
                "É... tá chato mesmo",
                "Bem complicadinho",
            ]))

        if lowered.startswith(("acho que sim", "acho que não", "talvez")):
            return self._with_variance(self._pick([
                "Você ainda tá hesitando",
                "Não tá convicto ainda",
                "Tem dúvida aí",
            ]))

        return self._with_variance(self._pick([
            "Tô aqui",
            "Pode falar",
            "Manda",
            "Diz aí",
        ]))