from __future__ import annotations

import random


class LenaResponseHumanizer:
    _last_memory_ack = ""
    _last_social = ""
    _last_style = ""
    _last_topic = ""
    _last_emotion_light = ""
    _last_emotion_heavy = ""

    @staticmethod
    def _pick(pool: list[str], attr: str) -> str:
        last = getattr(LenaResponseHumanizer, attr)
        choices = [x for x in pool if x != last] or pool
        chosen = random.choice(choices)
        setattr(LenaResponseHumanizer, attr, chosen)
        return chosen

    @staticmethod
    def acknowledge_memory_store(style: str = "neutral") -> str:
        pools = {
            "neutral": [
                "beleza, guardei.",
                "ficou salvo aqui.",
                "registrado.",
                "anotado.",
            ],
            "casual": [
                "beleza, guardei.",
                "tá guardado.",
                "fechou, deixei salvo.",
                "show, anotei.",
            ],
            "intimate": [
                "guardei isso aqui.",
                "deixei salvo comigo.",
                "tá guardado.",
                "anotei sim.",
            ],
            "slang": [
                "fechou, guardei.",
                "boa, deixei salvo.",
                "tá comigo isso.",
                "anotei aqui.",
            ],
        }
        return LenaResponseHumanizer._pick(pools.get(style, pools["neutral"]), "_last_memory_ack")

    @staticmethod
    def emotional_ack(style: str = "neutral", heavy: bool = False) -> str:
        if heavy:
            pools = {
                "neutral": [
                    "isso tá soando mais acumulado do que pontual",
                    "tem mais peso aí do que só uma manhã ruim",
                    "isso parece desgaste juntando faz tempo",
                ],
                "casual": [
                    "isso tá com cara de coisa acumulada",
                    "tem um peso maior aí rolando",
                    "isso não parece ser só de hoje",
                ],
                "intimate": [
                    "isso vem pesando há mais tempo né",
                    "não tá parecendo só um momento solto",
                    "tem um acúmulo aí dentro",
                ],
                "slang": [
                    "isso já tá com cara de acúmulo",
                    "aí tem mais coisa embolada",
                    "isso não é só um dia ruim não",
                ],
            }
            return LenaResponseHumanizer._pick(pools.get(style, pools["neutral"]), "_last_emotion_heavy")

        pools = {
            "neutral": [
                "Entendi. Tá sem energia pra tudo",
                "Putz... acordou sem bateria nenhuma",
                "Hum... bateu aquele vazio no ritmo",
                "Deu uma murchada forte então",
            ],
            "casual": [
                "vish, acordou sem gás nenhum",
                "deu uma drenada legal então",
                "tá num ritmo bem murcho hoje",
                "sem bateria total então",
            ],
            "intimate": [
                "entendi... hoje tu acordou bem sem força",
                "tá pesado até pra começar as coisas né",
                "parece que teu corpo não entrou no dia",
                "tu tá sem arranque nenhum hoje",
            ],
            "slang": [
                "ih, acordou zerado então",
                "bateu uma drenada braba",
                "sem gasolina nenhuma hoje",
                "murchou bonito o sistema",
            ],
        }
        return LenaResponseHumanizer._pick(pools.get(style, pools["neutral"]), "_last_emotion_light")

    @staticmethod
    def social_invite(style: str = "neutral") -> str:
        pools = {
            "neutral": [
                "Claro. Tô ouvindo",
                "Bora. Tô contigo",
                "Vamos sim. Me fala",
            ],
            "casual": [
                "bora, manda aí",
                "tô contigo, fala",
                "vamos, te ouvindo",
            ],
            "intimate": [
                "fala comigo, tô aqui",
                "pode falar, tô te ouvindo",
                "vem, me conta",
            ],
            "slang": [
                "manda aí, tô junto",
                "bora, solta",
                "fala que eu tô aqui",
            ],
        }
        return LenaResponseHumanizer._pick(pools.get(style, pools["neutral"]), "_last_social")

    @staticmethod
    def style_shift_ack(style: str = "neutral") -> str:
        pools = {
            "neutral": [
                "Fechou. Mais humana então",
                "Boa, vou ficar mais natural",
                "Fechado, vou falar mais solta",
            ],
            "casual": [
                "beleza, vou soltar mais",
                "boa, vou ficar mais leve",
                "fechou, menos travada então",
            ],
            "intimate": [
                "tá, vou falar mais pertinho contigo",
                "beleza, vou ficar mais natural contigo",
                "vou deixar mais leve sim",
            ],
            "slang": [
                "fechou, vou ficar menos robótica",
                "boa, vou desenferrujar",
                "beleza, vou falar mais na moral",
            ],
        }
        return LenaResponseHumanizer._pick(pools.get(style, pools["neutral"]), "_last_style")

    @staticmethod
    def topic_shift_ack(style: str = "neutral") -> str:
        pools = {
            "neutral": [
                "Bora. Joga outro tema",
                "Beleza, muda aí",
                "Fechou, qual agora",
            ],
            "casual": [
                "bora, manda outro",
                "beleza, puxa outro assunto",
                "vai, próximo tema",
            ],
            "intimate": [
                "tá bom, vamos pra outro",
                "certo, muda o assunto",
                "vamos, outro tema então",
            ],
            "slang": [
                "manda o próximo",
                "bora pra outra",
                "solta outro assunto",
            ],
        }
        return LenaResponseHumanizer._pick(pools.get(style, pools["neutral"]), "_last_topic")
