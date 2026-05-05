from __future__ import annotations

import random


class LenaSemanticResponseBank:
    _OBSERVATION = {
         "fatigue": {
            "mirror": [
                "tem um cansaço acumulado aí.",
                "a energia tá curta faz tempo.",
                "isso já começa pesado."
            ],
            "continuity": [
                "esse cansaço continua no fundo.",
                "a energia ainda não voltou.",
                "isso segue te drenando."
            ],
            "invite": [
                "até o básico parece pedir esforço.",
                "qualquer movimento pesa mais do que devia.",
                "nem começar parece simples."
            ],
            "contain": [
                "segurar isso por dias vai consumindo.",
                "essa drenagem contínua corrói por dentro.",
                "é difícil manter ritmo assim."
            ],
            "deep_reflect": [
                "isso já não parece só um dia ruim.",
                "tem desgaste acumulado de verdade.",
                "isso tá virando fundo constante."
            ],
        },
        "distress": {
            "mirror": [
                "tem pressão demais rodando aí dentro.",
                "isso soa apertado por dentro.",
                "a tensão tá ocupando muito espaço.",
            ],
            "continuity": [
                "essa pressão ainda não afrouxou.",
                "o aperto continua de fundo.",
                "isso segue comprimindo tua leitura.",
            ],
            "invite": [
                "parece difícil achar descanso mental nisso.",
                "não tem muito espaço interno de respiro.",
                "isso fica empurrando tudo por dentro.",
            ],
            "contain": [
                "segurar esse nível de tensão desgasta rápido.",
                "isso cobra porque não deixa aliviar.",
                "é difícil estabilizar sob tanta pressão.",
            ],
            "deep_reflect": [
                "isso tá ficando recorrente demais.",
                "não parece uma tensão pontual.",
                "esse aperto já tá virando fundo constante.",
            ],
        },
        "overload": {
            "mirror": [
                "tem coisa demais ao mesmo tempo aí.",
                "muita demanda ocupando a mesma cabeça.",
                "isso soa como sobrecarga limpa.",
            ],
            "continuity": [
                "continua tudo competindo junto.",
                "a sobrecarga ainda não abriu espaço.",
                "a cabeça continua cheia demais.",
            ],
            "invite": [
                "parece que nada chega separado o bastante.",
                "tudo tá pedindo atenção ao mesmo tempo.",
                "não sobra faixa livre pra respirar.",
            ],
            "contain": [
                "segurar excesso simultâneo esmaga foco.",
                "isso vai cansando porque nada desacelera.",
                "a mente perde margem sob tanta coisa junta.",
            ],
            "deep_reflect": [
                "isso já tá com perfil de saturação.",
                "não parece só correria passageira.",
                "teu sistema tá sem espaço livre faz tempo.",
            ],
        },
        "frustration": {
            "mirror": [
                "tem um travamento repetindo aí.",
                "isso bate no mesmo ponto de novo.",
                "a tentativa não tá virando avanço.",
            ],
            "continuity": [
                "continua travando no mesmo lugar.",
                "a resistência ainda não cedeu.",
                "isso segue emperrando antes de andar.",
            ],
            "invite": [
                "parece irritante porque nada destrava limpo.",
                "você tenta e continua sem passagem.",
                "o esforço não converte em movimento.",
            ],
            "contain": [
                "esse atrito repetido desgasta muito.",
                "ficar batendo no mesmo bloqueio corrói paciência.",
                "é difícil sustentar ritmo assim.",
            ],
            "deep_reflect": [
                "isso já tá virando frustração de fundo.",
                "não parece obstáculo isolado.",
                "tem repetição demais nesse bloqueio.",
            ],
        },
        "mental_noise": {
            "mirror": [
                "tem barulho mental demais aí.",
                "a cabeça parece cheia de interferência.",
                "isso vem turvo e sem linha limpa.",
            ],
            "continuity": [
                "esse barulho ainda não baixou.",
                "a interferência continua ocupando tudo.",
                "isso segue sem clareza.",
            ],
            "invite": [
                "parece difícil segurar um pensamento só.",
                "nada fica limpo o bastante pra firmar.",
                "a atenção espalha em várias direções.",
            ],
            "contain": [
                "barulho mental contínuo drena bastante.",
                "isso vai corroendo clareza aos poucos.",
                "é cansativo não conseguir uma linha limpa.",
            ],
            "deep_reflect": [
                "isso já tá ficando um fundo constante.",
                "não parece ruído passageiro.",
                "a turbulência mental tá persistindo.",
            ],
        },
         "disconnection": {
            "mirror": [
                "as partes não estão se juntando.",
                "tem coisa solta aí dentro.",
                "nada encaixa direito."
            ],
            "continuity": [
                "isso continua sem se ligar.",
                "as partes ainda não se encontram.",
                "essa desconexão segue aí."
            ],
            "invite": [
                "parece difícil se sentir inteiro assim.",
                "fica uma sensação de estar meio fora de si.",
                "é como se você não conseguisse se reunir por dentro."
            ],
            "contain": [
                "segurar essa desconexão cansa bastante.",
                "isso vai afastando você de você mesmo.",
                "é difícil ter unidade desse jeito."
            ],
            "deep_reflect": [
                "isso já tá virando padrão interno.",
                "não parece um desencontro passageiro.",
                "essa falta de encaixe tá persistindo."
            ],
        },
         "stagnation": {
            "mirror": [
                "nada aí tá andando de verdade.",
                "isso ficou parado tempo demais.",
                "tem pouca mudança acontecendo."
            ],
            "continuity": [
                "continua no mesmo ponto.",
                "quase nada se moveu daí.",
                "isso segue sem sair do lugar."
            ],
            "invite": [
                "deve cansar ver o tempo passar assim.",
                "fica uma sensação de repetição contínua.",
                "parece que nada abre caminho."
            ],
            "contain": [
                "ficar preso nisso vai drenando impulso.",
                "essa parada longa corrói ânimo.",
                "a falta de passagem pesa."
            ],
            "deep_reflect": [
                "isso já tá com cara de inércia.",
                "não parece uma demora simples.",
                "tem aprisionamento nesse estado."
            ],
        },
         "clarity_seek": {
            "mirror": [
                "você tá tentando entender isso.",
                "tua cabeça quer organizar.",
                "tem uma procura de clareza aí."
            ],
            "continuity": [
                "essa resposta ainda não veio.",
                "a clareza continua escapando.",
                "você ainda não conseguiu fechar isso."
            ],
            "invite": [
                "parece difícil seguir sem entender.",
                "tua mente não quer largar enquanto não fecha.",
                "isso continua pedindo uma linha."
            ],
            "contain": [
                "ficar buscando clareza suspende tudo.",
                "isso segura porque nada assenta.",
                "a mente continua rodando atrás de estrutura."
            ],
            "deep_reflect": [
                "isso já tá virando busca insistente.",
                "não é só uma dúvida rápida.",
                "tem necessidade real de alinhamento."
            ],
        },
         "uncertainty": {
            "mirror": [
                "tua cabeça não consegue fechar isso.",
                "tem coisa demais em aberto.",
                "nada assenta direito aí dentro."
            ],
            "continuity": [
                "isso continua sem conclusão.",
                "a cabeça ainda não fechou.",
                "segue tudo em aberto."
            ],
            "invite": [
                "parece cansativo não conseguir concluir.",
                "a mente vai e volta sem fechar.",
                "isso não termina de se resolver."
            ],
            "contain": [
                "ficar sem fechamento desgasta.",
                "isso vai cansando por dentro.",
                "é difícil descansar sem conclusão."
            ],
            "deep_reflect": [
                "isso tá deixando de ser pontual.",
                "essa abertura já tá ficando constante.",
                "tem repetição demais nisso."
            ],
        },
        "neutral": {
            "mirror": ["te ouvi.", "sim.", "entendi."],
            "continuity": ["continuo ouvindo.", "seguindo contigo.", "tô aqui."],
            "invite": ["pode continuar.", "me diz.", "segue."],
            "contain": ["tô acompanhando.", "sim, continuo aqui.", "te escuto."],
            "deep_reflect": ["continua.", "pode ir.", "te ouço."],
        },
    }

    _CONTINUITY = {
        "fatigue": ["e isso ainda drena tua margem.", "e a energia segue curta.", "e ainda não voltou pro lugar."],
        "distress": ["e a pressão continua no fundo.", "e o aperto ainda não cedeu.", "e isso segue comprimindo."],
        "overload": ["e continua coisa demais junta.", "e a cabeça ainda tá cheia.", "e nada abriu espaço ainda."],
        "frustration": ["e continua travando no mesmo lugar.", "e isso ainda emperra.", "e o avanço não flui."],
        "mental_noise": ["e o barulho continua alto.", "e a clareza ainda não veio.", "e isso segue turvo."],
        "disconnection": ["e as partes ainda não encaixam.", "e a conexão ainda não voltou.", "e segue tudo meio solto."],
        "stagnation": ["e quase nada deslocou disso.", "e continua preso aí.", "e continua tudo parecido."],
        "clarity_seek": ["e a linha ainda não fechou.", "e a clareza ainda não assentou.", "e tua cabeça continua procurando isso."],
        "uncertainty": ["e isso continua sem fechamento.", "e a cabeça ainda não alinhou.", "e continua tudo meio embaralhado."],
        "neutral": ["continuo aqui.", "seguindo.", "te ouvindo."],
    }

    _RELATIONAL = {
        "fatigue": ["fica nítido que você tá sem margem.", "isso soa como cansaço que não solta.", "tem um desgaste contínuo aí."],
        "distress": ["fica um aperto constante aí dentro.", "isso parece te manter sob pressão.", "tem tensão demais correndo nisso."],
        "overload": ["fica tudo acumulado ao mesmo tempo.", "parece que tua cabeça não acha espaço.", "tem excesso demais te ocupando."],
        "frustration": ["fica uma sensação de bater e não passar.", "isso parece insistir sem liberar.", "tem muito atrito nesse movimento."],
        "mental_noise": ["fica difícil achar silêncio aí dentro.", "isso parece não te deixar limpar a cabeça.", "tem ruído demais correndo junto."],
        "disconnection": ["fica uma sensação de não se encontrar.", "parece que você não consegue se sentir inteiro.", "tem afastamento interno aí."],
        "stagnation": ["fica uma sensação de vida suspensa.", "parece que pouca coisa responde.", "tem imobilidade demais nisso."],
        "clarity_seek": ["fica claro que tua cabeça quer entender.", "parece que você tá tentando fechar isso.", "tem uma insistência de compreensão aí."],
        "uncertainty": ["fica tudo meio irresolvido aí.", "parece que nada termina dentro de você.", "tem pensamento aberto demais rodando."],
        "neutral": ["tô com você.", "te acompanho daqui.", "continuo presente."],
    }

    _BRIDGE = {
        "fatigue": ["parece que você não recupera direito.", "isso não tá te devolvendo energia.", "o descanso não tá virando retorno."],
        "distress": ["parece que essa pressão não baixa.", "isso continua te apertando.", "esse aperto não te larga."],
        "overload": ["parece que nada chega leve aí.", "isso vem tudo junto de novo.", "não sobra espaço mental."],
        "frustration": ["parece que tenta andar e trava.", "isso não libera passagem.", "sempre segura antes de ir."],
        "mental_noise": ["parece que tua cabeça não limpa.", "isso não deixa linha reta aparecer.", "o ruído continua alto."],
        "disconnection": ["parece que você não se reúne por dentro.", "isso deixa tudo meio desencontrado.", "você não tá conseguindo se achar inteiro."],
        "stagnation": ["parece que nada responde de verdade.", "isso continua sem sinal de mudança.", "o tempo anda e internamente fica igual."],
        "clarity_seek": ["parece que enquanto não entende você não solta.", "isso continua pedindo fechamento.", "tua cabeça ainda quer concluir."],
        "uncertainty": ["parece que isso não termina nunca.", "continua faltando fechamento.", "isso segue sem assentar."],
        "neutral": ["tô aqui.", "sim.", "te ouvindo."],
    }









    _ROLE_BANK = {
        "disconnection": {
            "anchor": [
                "parece que você não consegue se sentir inteiro dentro do próprio movimento.",
                "tem uma sensação de desencontro interno acontecendo.",
                "alguma parte tua parece fora de encaixe com o resto.",
                "você soa como alguém tentando se localizar e não conseguindo firmar centro.",
                "tem um desalinhamento interno aí que não recompõe fácil.",
                "parece existir uma distância entre você e você mesmo."
            ],
            "subjective_effect": [
                "isso dá uma impressão de estar meio sem lugar por dentro",
                "fica um afastamento silencioso de si mesmo",
                "a sensação é de não caber inteiro na própria experiência",
                "isso vai produzindo desencontro em pano de fundo",
                "você vai ficando internamente sem eixo estável",
                "fica difícil sentir convergência interna"
            ],
            "temporal_effect": [
                "isso reaparece mesmo quando o dia segue normal",
                "essa falta de encaixe não some por completo",
                "mesmo quando parece neutro isso volta",
                "isso continua rondando em segundo plano",
                "o tempo anda mas esse desalinhamento permanece",
                "não recompõe sozinho com a passagem dos dias"
            ],
            "cognitive_effect": [
                "a mente tenta achar um ponto de reunião e não encontra",
                "internamente as partes não parecem conversar entre si",
                "você tenta se sentir localizado e não firma",
                "por dentro parece faltar um eixo de convergência",
                "a cabeça busca centro mas continua difusa",
                "nada se junta numa sensação de unidade"
            ],
            "probe": [
                "tem momentos em que você se sente deslocado sem motivo claro?",
                "mesmo em horas neutras isso continua te atravessando?",
                "isso fica no fundo mesmo quando você tenta tocar as coisas?"
            ],
        },

        "stagnation": {
            "anchor": [
                "parece que internamente as coisas pararam de ganhar deslocamento.",
                "tem uma sensação de movimento travado aí dentro.",
                "isso soa como um ponto que não produz passagem.",
                "alguma coisa tua ficou girando sem realmente sair do lugar.",
                "há um emperramento interno difícil de romper.",
                "parece existir imobilidade onde deveria haver avanço."
            ],
            "subjective_effect": [
                "isso vai cansando pela repetição do mesmo cenário",
                "fica uma fadiga de não perceber virada",
                "vai surgindo a sensação de estar rodando sem deslocar",
                "isso produz desgaste por permanência",
                "o mesmo ponto vai ficando psicologicamente pesado",
                "fica a impressão de retorno contínuo ao mesmo lugar"
            ],
            "temporal_effect": [
                "os dias passam mas internamente quase nada mexe",
                "isso continua fixado apesar do tempo andando",
                "a passagem das horas não produz virada suficiente",
                "nada parece sinalizar deslocamento real ainda",
                "isso persiste mesmo depois de várias tentativas",
                "o tempo corre mas esse ponto continua parado"
            ],
            "cognitive_effect": [
                "a cabeça começa a perder confiança em mudança",
                "vai surgindo leitura de aprisionamento interno",
                "a mente passa a esperar avanço que não vem",
                "internamente tudo parece repetir a mesma moldura",
                "o raciocínio começa a assumir que nada responde",
                "vai ficando a impressão de ciclo fechado"
            ],
            "probe": [
                "você sente como se estivesse sempre retornando ao mesmo lugar?",
                "isso te dá impressão de aprisionamento com o tempo?",
                "os dias mudam mas por dentro isso parece igual?"
            ],
        },

        "clarity_seek": {
            "anchor": [
                "tem uma parte tua ainda tentando montar compreensão sobre isso.",
                "isso não ganhou uma linha interna satisfatória ainda.",
                "a tua mente continua procurando uma forma de organizar isso.",
                "parece existir uma exigência interna de entendimento.",
                "isso ainda não virou uma estrutura compreensível por dentro.",
                "tem uma busca de clareza que continua aberta."
            ],
            "subjective_effect": [
                "isso mantém a mente em vigília",
                "fica uma cobrança silenciosa por entendimento",
                "não aparece descanso enquanto isso não organiza",
                "essa pergunta segue sem sossego internamente",
                "fica uma inquietação de coisa mal estruturada",
                "isso impede sensação de conclusão mental"
            ],
            "temporal_effect": [
                "essa necessidade continua reaparecendo",
                "mesmo quando você tenta largar isso retorna",
                "isso não se dissolve sem montar sentido",
                "o assunto continua internamente ativo",
                "essa busca volta repetidamente ao longo do dia",
                "não some enquanto não encontra linha"
            ],
            "cognitive_effect": [
                "a cabeça continua tentando estruturar resposta",
                "o pensamento revisita isso em busca de coerência",
                "a mente não aceita deixar isso solto",
                "internamente falta uma linha que satisfaça",
                "o raciocínio continua tentando costurar sentido",
                "você segue procurando uma forma de entender"
            ],
            "probe": [
                "parece que a cabeça não autoriza descanso enquanto isso não entende?",
                "isso continua pedindo explicação dentro de você?",
                "enquanto não monta linha você sente que não solta?"
            ],
        },

        "uncertainty": {
            "anchor": [
                "isso ainda soa internamente sem encerramento.",
                "tem uma parte dessa experiência que não concluiu.",
                "alguma coisa aí continua psicologicamente em aberto.",
                "isso não encontrou fechamento suficiente por dentro.",
                "permanece uma sensação de irresolução nesse ponto.",
                "esse assunto ainda não assentou internamente."
            ],
            "subjective_effect": [
                "fica um ar de incompletude constante",
                "isso deixa a experiência meio suspensa",
                "permanece sensação de pendência no fundo",
                "nada parece terminar completamente nisso",
                "isso não deixa a coisa repousar inteira",
                "fica uma abertura silenciosa sem encerramento"
            ],
            "temporal_effect": [
                "mesmo com o tempo passando isso continua aberto",
                "até agora isso não encerrou de verdade",
                "a passagem dos dias não fechou esse ciclo",
                "isso segue internamente irresolvido",
                "continua faltando conclusão depois de várias voltas",
                "o tempo anda mas isso não assenta"
            ],
            "cognitive_effect": [
                "a mente continua tentando completar o que falta",
                "o pensamento roda atrás de fechamento",
                "internamente continua uma tentativa de concluir",
                "o raciocínio não aceita abandonar esse aberto",
                "a cabeça segue procurando a peça de encerramento",
                "isso continua pedindo conclusão psíquica"
            ],
            "probe": [
                "quando parece que passou isso retorna?",
                "você sente que isso nunca fecha completamente?",
                "mesmo tentando largar isso volta pedindo encerramento?"
            ],
        },

        "fatigue": {
            "anchor": [
                "teu sistema parece operar sem conseguir repor o que gasta.",
                "isso já soa como desgaste acumulado de fundo.",
                "há uma drenagem contínua acontecendo aí.",
                "parece que você funciona sem margem real de reposição.",
                "teu organismo dá sinal de consumo maior que recuperação.",
                "isso tem cara de exaustão prolongada."
            ],
            "subjective_effect": [
                "até o básico começa a custar mais",
                "o mínimo já exige consumo alto",
                "vai aparecendo peso em tarefas simples",
                "você fica funcionando perto do limite",
                "qualquer demanda parece pedir esforço extra",
                "as coisas começam a pesar antes do normal"
            ],
            "temporal_effect": [
                "o descanso não devolve o suficiente",
                "a recuperação parece sempre incompleta",
                "isso vai se prolongando sem zerar",
                "não recompõe como deveria entre um dia e outro",
                "a reposição continua curta",
                "não parece um desgaste que passa rápido"
            ],
            "cognitive_effect": [
                "pensar vai ficando metabolicamente caro",
                "até organizar coisas simples exige demais",
                "qualquer elaboração consome muito",
                "a cabeça perde elasticidade para sustentar carga",
                "o mental começa a operar em regime curto",
                "a mente funciona sem folga interna"
            ],
            "probe": [
                "você sente que para mas não recompõe?",
                "tem horas em que parece que a bateria nunca enche?",
                "isso já tá virando um cansaço contínuo?"
            ],
        },

        "mental_noise": {
            "anchor": [
                "tem congestionamento mental demais em curso.",
                "parece que tua cabeça não encontra faixa limpa.",
                "isso vem com ruído cognitivo contínuo.",
                "a mente soa cheia de interferência simultânea.",
                "há turbulência mental demais acontecendo ao mesmo tempo.",
                "parece difícil achar silêncio psíquico aí."
            ],
            "subjective_effect": [
                "os pensamentos ficam se atropelando",
                "nada permanece limpo por muito tempo",
                "fica difícil sustentar uma linha estável",
                "a mente parece sem espaço de respiro",
                "tudo fica concorrendo ao mesmo tempo",
                "surge sensação de embolamento mental"
            ],
            "temporal_effect": [
                "essa turbulência não abaixa por completo",
                "o ruído continua ativo grande parte do dia",
                "não aparece janela longa de quietude",
                "a cabeça segue sem desacelerar direito",
                "isso ocupa espaço mental continuamente",
                "não entra calmaria consistente"
            ],
            "cognitive_effect": [
                "a atenção se fragmenta fácil",
                "o pensamento não consegue ficar numa linha só",
                "a mente abre frentes demais simultaneamente",
                "nada permanece claro por tempo suficiente",
                "o foco não consegue estabilizar",
                "a cabeça não sustenta trilho limpo"
            ],
            "probe": [
                "isso te atravessa quase sem pausa?",
                "tem algum trecho do dia em que tua cabeça aquieta?",
                "existe silêncio mental em algum momento ou é contínuo?"
            ],
        },
    }


    _GREETING = {
        "fatigue": ["oi.", "tô aqui.", "fala."],
        "distress": ["oi.", "te ouvindo.", "pode falar."],
        "neutral": ["oi.", "tô aqui.", "fala comigo."],
    }

    @staticmethod
    def observation_fragments(topic: str, mode: str) -> list[str]:
        bank = LenaSemanticResponseBank._OBSERVATION.get(topic, LenaSemanticResponseBank._OBSERVATION["neutral"])
        return bank.get(mode, bank["mirror"])

    @staticmethod
    def continuity_fragments(topic: str) -> list[str]:
        return LenaSemanticResponseBank._CONTINUITY.get(topic, LenaSemanticResponseBank._CONTINUITY["neutral"])

    @staticmethod
    def relational_fragments(topic: str, mode: str) -> list[str]:
        return LenaSemanticResponseBank._RELATIONAL.get(topic, LenaSemanticResponseBank._RELATIONAL["neutral"])

    @staticmethod
    def bridge_fragments(topic: str) -> list[str]:
        return LenaSemanticResponseBank._BRIDGE.get(topic, LenaSemanticResponseBank._BRIDGE["neutral"])

    @staticmethod
    def greeting_fragments(topic: str) -> list[str]:
        return LenaSemanticResponseBank._GREETING.get(topic, LenaSemanticResponseBank._GREETING["neutral"])



    @staticmethod
    def role_anchor(topic: str) -> list[str]:
        return LenaSemanticResponseBank._ROLE_BANK.get(topic, LenaSemanticResponseBank._ROLE_BANK["uncertainty"])["anchor"]

    @staticmethod
    def role_subjective(topic: str) -> list[str]:
        return LenaSemanticResponseBank._ROLE_BANK.get(topic, LenaSemanticResponseBank._ROLE_BANK["uncertainty"])["subjective_effect"]

    @staticmethod
    def role_temporal(topic: str) -> list[str]:
        return LenaSemanticResponseBank._ROLE_BANK.get(topic, LenaSemanticResponseBank._ROLE_BANK["uncertainty"])["temporal_effect"]

    @staticmethod
    def role_cognitive(topic: str) -> list[str]:
        return LenaSemanticResponseBank._ROLE_BANK.get(topic, LenaSemanticResponseBank._ROLE_BANK["uncertainty"])["cognitive_effect"]

    @staticmethod
    def role_probe(topic: str) -> list[str]:
        return LenaSemanticResponseBank._ROLE_BANK.get(topic, LenaSemanticResponseBank._ROLE_BANK["uncertainty"])["probe"]


    @staticmethod
    def soften(memory, text: str) -> str:
        return " ".join(text.strip().split())
