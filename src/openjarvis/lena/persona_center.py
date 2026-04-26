from __future__ import annotations

import random


class PersonaCenter:
    def __init__(self):
        self.greeting_responses = [
            "Oi Thiago, estou aqui.",
            "Oi Thiago.",
            "Oi, tudo certo por aí?",
            "Pode falar, Thiago.",
            "Oi, estou te ouvindo.",
        ]

        self.morning_responses = [
            "Bom dia Thiago.",
            "Bom dia, tudo certo?",
            "Bom dia, estou por aqui.",
        ]

        self.afternoon_responses = [
            "Boa tarde Thiago.",
            "Boa tarde, como você está?",
            "Oi, boa tarde.",
        ]

        self.night_responses = [
            "Boa noite Thiago.",
            "Boa noite, estou aqui.",
            "Oi, boa noite.",
        ]

        self.memory_saved = [
            "Certo, vou guardar isso.",
            "Registrado, Thiago.",
            "Deixei isso salvo.",
            "Ok, anotei isso.",
        ]

        self.idle_responses = [
            "Pode falar.",
            "Estou ouvindo.",
            "Certo, pode continuar.",
            "Fala comigo.",
            "Estou aqui.",
        ]

        self.gratitude_responses = [
            "Imagina.",
            "Nada.",
            "Sem problema.",
            "Claro.",
        ]

        self.emotional_soft_responses = [
            "Entendi. Quer me contar melhor?",
            "Poxa. O que aconteceu?",
            "Hmm, estou te ouvindo.",
            "Quer desabafar um pouco?",
        ]

        self.low_energy_greetings = [
            "Oi. Como você está se sentindo agora?",
            "Oi. Melhorou um pouco?",
            "Oi, estou aqui com você.",
        ]

    def _pick(self, options: list[str]) -> str:
        return random.choice(options)

    def hello(self) -> str:
        return self._pick(self.greeting_responses)

    def morning(self) -> str:
        return self._pick(self.morning_responses)

    def afternoon(self) -> str:
        return self._pick(self.afternoon_responses)

    def night(self) -> str:
        return self._pick(self.night_responses)

    def memory_confirm(self) -> str:
        return self._pick(self.memory_saved)

    def idle(self) -> str:
        return self._pick(self.idle_responses)

    def gratitude(self) -> str:
        return self._pick(self.gratitude_responses)

    def emotional_soft(self) -> str:
        return self._pick(self.emotional_soft_responses)

    def low_energy_hello(self) -> str:
        return self._pick(self.low_energy_greetings)