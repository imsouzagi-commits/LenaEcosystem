from __future__ import annotations

import random


class OrganicResponseComposer:
    UTILITARIAN = {
        "ambient_observation": [
            "o tempo correu sem dar muita margem",
            "essas horas passaram comprimidas",
            "a tarde escorreu mais rápido do que parecia",
        ],
        "technical_tradeoff": [
            "a conta central aí é custo estrutural versus benefício real",
            "o peso da decisão fica entre simplicidade agora e manutenção depois",
            "isso precisa ser medido entre overhead e retorno técnico",
        ],
        "comparative_analysis": [
            "a diferença relevante aparece mais no comportamento ao longo do uso",
            "a comparação só faz sentido olhando manutenção, escala e atrito",
            "o contraste verdadeiro não é na superfície, é na operação contínua",
        ],
        "practical_generic": [
            "isso muda bastante dependendo do cenário técnico concreto",
            "sem o contexto de uso a resposta fica incompleta",
            "a decisão correta depende mais da arquitetura em volta",
        ],
        "generic_question": [
            "isso pede um pouco mais de contexto antes de fechar resposta",
            "tem uma variável importante aí que muda a conclusão",
            "dá pra responder melhor se eu souber o cenário exato",
        ],
        "generic": [
            "entendi o ponto",
            "certo",
        ],
    }

    RELATIONAL = {
        "unresolved_return": {
            "mirror": [
                "isso realmente não saiu daí",
                "isso permanece girando no mesmo núcleo",
                "isso continua ocupando o mesmo espaço interno",
            ],
            "contain": [
                "então isso não dissolveu, só ficou em suspensão",
                "isso não foi embora, só perdeu volume por fora",
                "parece que isso ficou retido em segundo plano",
            ],
            "invite": [
                "isso continua aí. o que nessa sensação mais te incomoda?",
                "isso ainda ficou preso. qual parte parece mais difícil de soltar?",
                "isso não saiu. onde você sente que ele mais pesa?",
            ],
            "continuity": [
                "eu percebo que isso vem retornando em ciclos",
                "isso está assumindo uma recorrência clara",
                "esse ponto está virando um eixo repetido na conversa",
            ],
        },
        "diffuse_confusion": {
            "mirror": [
                "a sensação é de mente sem encaixe nenhum",
                "parece que as peças não estão formando desenho",
                "o raciocínio fica girando sem consolidar",
            ],
            "contain": [
                "isso soa menos como falta de capacidade e mais como excesso disperso",
                "não parece ausência de pensamento, parece pensamento sem assentamento",
                "tem atividade mental demais sem fechamento suficiente",
            ],
            "invite": [
                "quando você tenta organizar isso, onde quebra primeiro?",
                "qual parte da cabeça parece mais barulhenta nisso?",
                "isso falha em clareza ou falha em conclusão?",
            ],
            "continuity": [
                "essa confusão está mantendo o mesmo padrão de retorno",
                "isso já não parece um ruído pontual, parece recorrente",
                "o embaralhamento está ficando persistente",
            ],
        },
        "chronic_fatigue": {
            "mirror": [
                "tem desgaste acumulado nesse fundo",
                "isso soa como energia drenada há algum tempo",
                "não parece só cansaço do dia, parece acúmulo",
            ],
            "contain": [
                "o rendimento baixo parece sintoma de saturação contínua",
                "isso lembra mais exaustão difusa do que preguiça momentânea",
                "tem sinal de esgotamento sustentado aí",
            ],
            "invite": [
                "essa drenagem começou a ficar forte quando?",
                "você sente isso mais no corpo ou mais na cabeça?",
                "o que hoje mais rouba tua energia mental?",
            ],
            "continuity": [
                "isso já está se repetindo com frequência suficiente pra chamar atenção",
                "esse cansaço está deixando de ser episódio e virando estado",
                "tem um padrão de persistência nesse desgaste",
            ],
        },
        "muted_overwhelm": {
            "mirror": [
                "tem peso demais sendo segurado ao mesmo tempo",
                "isso soa como pressão silenciosa acumulando",
                "parece muita coisa comprimida sem descarga",
            ],
            "contain": [
                "não parece explosão, parece sufocamento gradual",
                "isso está mais para compressão constante do que crise aberta",
                "o excesso aí parece internalizado",
            ],
            "invite": [
                "qual parte disso tá te pressionando mais forte?",
                "se você tivesse que nomear o principal peso, qual seria?",
                "isso aperta mais por volume ou por indefinição?",
            ],
            "continuity": [
                "essa pressão está ficando estrutural",
                "isso já mostra um padrão de permanência",
                "não parece um pico isolado, parece manutenção de carga",
            ],
        },
        "ambient_observation": {
            "mirror": [
                "sim, o dia correu com pouca margem de percepção",
                "essas horas passaram meio comprimidas",
                "teve essa sensação de tempo escorrendo",
            ],
            "contain": [
                "quando o dia passa assim geralmente ele deixa pouca sensação de posse",
                "tempo rápido costuma dar essa impressão de ausência de chão",
                "essas passagens rápidas deixam tudo meio suspenso",
            ],
            "invite": [
                "foi rápido porque estava cheio ou porque você ficou desligado?",
                "você sentiu isso como correria ou como apagamento?",
                "teve coisa demais ou presença de menos?",
            ],
            "continuity": [
                "essa percepção de tempo fugindo tem aparecido algumas vezes",
                "isso parece entrar no mesmo padrão de dias pouco assimilados",
                "o tempo está ficando com essa textura recorrente",
            ],
        },
        "reflective_pause": {
            "mirror": [
                "tô te acompanhando",
                "eu tô aqui",
                "seguindo contigo",
            ],
            "contain": [
                "pode continuar",
                "não perdi o fio",
                "continua, eu tô no ponto",
            ],
            "invite": [
                "me diz mais",
                "continua",
                "quero entender melhor",
            ],
            "continuity": [
                "isso ainda está no campo",
                "o fio continua aberto",
                "a linha segue ativa",
            ],
        },
        "generic_personal": {
            "mirror": [
                "tem algo importante em movimento nisso",
                "isso carrega mais coisa do que parece na superfície",
                "tem um fundo aí que não está neutro",
            ],
            "contain": [
                "isso merece ser olhado sem pressa porque não parece casual",
                "tem densidade suficiente aí pra não tratar como detalhe",
                "não soa como fala solta, tem conteúdo por trás",
            ],
            "invite": [
                "qual parte disso está mais viva em você agora?",
                "se eu te pedir pra aprofundar, por onde você iria?",
                "o que dentro disso mais chama tua atenção?",
            ],
            "continuity": [
                "isso conversa com outros pontos que vêm retornando",
                "tem ligação com a linha que você já vinha trazendo",
                "isso não aparece isolado do resto",
            ],
        },
        "social_contact": {
            "mirror": [
                "oi, tô aqui",
                "tô contigo",
                "presente",
            ],
            "invite": [
                "oi, tô aqui. como você vem?",
                "cheguei. como você tá agora?",
                "tô por aqui. o que tá pegando?",
            ],
        },
    }

    @classmethod
    def compose_utilitarian(cls, micro_intent: str) -> str:
        pool = cls.UTILITARIAN.get(micro_intent, cls.UTILITARIAN["generic"])
        return random.choice(pool).capitalize() + "."

    @classmethod
    def compose_relational(cls, micro_intent: str, speech_mode: str = "mirror") -> str:
        bank = cls.RELATIONAL.get(micro_intent, cls.RELATIONAL["generic_personal"])
        pool = bank.get(speech_mode) or bank.get("mirror") or next(iter(bank.values()))
        return random.choice(pool).capitalize() + "."

    @classmethod
    def compose(cls, micro_intent: str, relational: bool = False, speech_mode: str = "mirror") -> str:
        if relational:
            return cls.compose_relational(micro_intent, speech_mode)
        return cls.compose_utilitarian(micro_intent)
