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
                "tem uma desconexão interna aí.",
                "alguma parte tua não tá se encontrando.",
                "você parece meio fora do próprio eixo.",
                "tem um desencontro interno acontecendo.",
                "alguma coisa em você não tá se juntando direito.",
                "parece que você não consegue se localizar inteiro."
            ],
            "subjective_effect": [
                "isso vai te deixando meio sem lugar por dentro",
                "fica uma sensação de desencontro em pano de fundo",
                "dá uma impressão de não caber direito em si",
                "você vai ficando internamente desalinhado",
                "fica difícil sentir unidade no próprio movimento",
                "isso produz um afastamento de si mesmo"
            ],
            "temporal_effect": [
                "isso não vai embora com facilidade",
                "essa sensação continua reaparecendo",
                "isso fica rondando mesmo quando você tenta tocar o dia",
                "mesmo em momentos neutros isso volta",
                "essa falta de encaixe continua se insinuando",
                "o tempo passa mas isso não recompõe"
            ],
            "cognitive_effect": [
                "tua cabeça tenta se localizar e não firma",
                "por dentro as partes não parecem encaixar",
                "você tenta se sentir inteiro e não consegue",
                "internamente parece faltar um ponto de reunião",
                "a mente busca um centro e não acha",
                "tudo parece sem convergência suficiente"
            ],
            "probe": [
                "isso te acompanha em pano de fundo?",
                "mesmo distraído isso continua aí?",
                "tem momentos em que você se sente deslocado sem motivo claro?",
            ],
        },

        "stagnation": {
            "anchor": [
                "tem uma sensação de parada aí.",
                "alguma coisa tua ficou sem deslocamento.",
                "isso parece parado por dentro.",
                "tem imobilidade demais nesse ponto.",
                "parece que internamente nada ganha passagem.",
                "isso tá com cara de coisa emperrada."
            ],
            "subjective_effect": [
                "vai dando um cansaço de continuar no mesmo lugar",
                "fica a impressão de que nada realmente vira",
                "isso faz tudo parecer meio emperrado",
                "você sente desgaste de repetição interna",
                "o mesmo cenário vai cansando por dentro",
                "fica uma fadiga de ausência de mudança"
            ],
            "temporal_effect": [
                "isso já dura mais do que devia",
                "o tempo passa e quase nada mexe nisso",
                "os dias andam mas internamente continua parecido",
                "a passagem do tempo não produz deslocamento real",
                "isso continua fixado apesar das tentativas",
                "nada parece sinalizar virada ainda"
            ],
            "cognitive_effect": [
                "tua mente começa a esperar mudança que não vem",
                "vai ficando a impressão de que nada responde",
                "por dentro parece sempre o mesmo cenário",
                "a cabeça perde confiança em avanço",
                "vai surgindo uma leitura de aprisionamento",
                "internamente tudo começa a parecer estático"
            ],
            "probe": [
                "isso tá te dando impressão de estar preso faz tempo?",
                "você sente os dias mudando mas isso não?",
                "parece que você tá sempre retornando ao mesmo lugar?",
            ],
        },

        "clarity_seek": {
            "anchor": [
                "tem uma necessidade de entender isso.",
                "alguma parte tua continua pedindo clareza.",
                "isso ainda não virou uma linha compreensível.",
                "tem uma busca de organização mental aí.",
                "isso ainda não ganhou forma dentro de você.",
                "a tua mente ainda quer montar sentido nisso."
            ],
            "subjective_effect": [
                "isso te deixa inquieto por dentro",
                "não tem descanso enquanto isso não organiza",
                "essa pergunta fica sem sossego internamente",
                "a sensação é de pensamento pendurado",
                "fica uma cobrança silenciosa por entendimento",
                "isso mantém a mente em vigília"
            ],
            "temporal_effect": [
                "isso continua voltando",
                "isso não se dissolve sozinho",
                "essa pergunta reaparece o tempo todo",
                "mesmo quando você tenta largar isso retorna",
                "isso insiste em reaparecer sem concluir",
                "o assunto continua internamente ativo"
            ],
            "cognitive_effect": [
                "tua mente fica revisitando isso",
                "o pensamento continua procurando fechamento",
                "tua cabeça volta nisso tentando montar sentido",
                "a mente não aceita deixar isso solto",
                "você continua tentando estruturar uma resposta",
                "internamente falta uma linha satisfatória"
            ],
            "probe": [
                "enquanto não entende isso você sente que não solta?",
                "isso continua pedindo explicação dentro de você?",
                "parece que a cabeça não autoriza descanso enquanto isso não fecha?",
            ],
        },

        "uncertainty": {
            "anchor": [
                "tem coisa sem resolução aí.",
                "isso ainda não encontrou fechamento interno.",
                "alguma parte disso continua aberta.",
                "tem pendência psicológica nesse ponto.",
                "isso não assentou de verdade.",
                "continua faltando encerramento aí dentro."
            ],
            "subjective_effect": [
                "isso deixa tudo meio em suspenso",
                "fica uma sensação de pendência no fundo",
                "isso não deixa a coisa assentar direito",
                "fica um ar de incompletude constante",
                "parece que nada termina internamente",
                "isso produz suspensão em pano de fundo"
            ],
            "temporal_effect": [
                "isso continua mesmo com o tempo passando",
                "os dias passam e isso continua aberto",
                "até agora isso não fechou de verdade",
                "a passagem do tempo não encerrou isso",
                "continua faltando conclusão mesmo depois de várias voltas",
                "isso segue internamente irresolvido"
            ],
            "cognitive_effect": [
                "tua cabeça continua tentando concluir",
                "o pensamento fica rodando atrás de fechamento",
                "isso continua pedindo encerramento por dentro",
                "a mente ainda procura a peça que falta",
                "internamente segue uma tentativa de completar isso",
                "o raciocínio não aceita abandonar esse aberto"
            ],
            "probe": [
                "isso volta mesmo quando você tenta largar?",
                "quando parece que passou isso retorna?",
                "você sente que isso nunca fecha completamente?",
            ],
        },

        "fatigue": {
            "anchor": [
                "tem um esgotamento de fundo aí.",
                "teu sistema parece sem reposição suficiente.",
                "isso já soa como desgaste acumulado.",
                "tem uma drenagem silenciosa em curso.",
                "parece cansaço além do normal.",
                "teu organismo tá operando sem muita sobra."
            ],
            "subjective_effect": [
                "qualquer coisa começa a pesar mais",
                "até o básico vai ficando custoso",
                "você fica funcionando perto do limite",
                "o mínimo já exige consumo alto",
                "vai aparecendo peso até em tarefas simples",
                "o dia inteiro começa a pedir esforço extra"
            ],
            "temporal_effect": [
                "a recuperação não vem direito",
                "isso não parece um cansaço passageiro",
                "teu corpo não recompõe como deveria",
                "o descanso não devolve margem suficiente",
                "a reposição parece sempre incompleta",
                "isso vai se prolongando sem zerar"
            ],
            "cognitive_effect": [
                "tua mente tá funcionando sem folga",
                "pensar vai ficando mais caro",
                "até organizar coisa simples exige demais",
                "a cabeça perde elasticidade",
                "qualquer elaboração já consome bastante",
                "o mental começa a operar em regime curto"
            ],
            "probe": [
                "você sente que descansa mas não recompõe?",
                "isso tá ficando contínuo já?",
                "tem horas em que parece que a bateria nunca volta cheia?",
            ],
        },

        "mental_noise": {
            "anchor": [
                "tem interferência demais aí dentro.",
                "tua cabeça parece sem faixa limpa.",
                "isso vem com ruído interno forte.",
                "o mental tá congestionado.",
                "parece difícil encontrar silêncio aí.",
                "tem turbulência cognitiva demais em curso."
            ],
            "subjective_effect": [
                "tudo fica meio embolado internamente",
                "fica difícil achar um pouco de silêncio",
                "a mente parece sem espaço de respiro",
                "os pensamentos se atropelam",
                "nada fica limpo o suficiente por muito tempo",
                "você não consegue uma linha estável"
            ],
            "temporal_effect": [
                "isso ocupa espaço há um tempo",
                "essa turbulência não abaixa direito",
                "não aparece uma calmaria de verdade",
                "o ruído continua ativo quase o dia inteiro",
                "não tem janela longa de quietude",
                "a cabeça segue sem desacelerar"
            ],
            "cognitive_effect": [
                "o pensamento não consegue ficar numa linha só",
                "a mente abre frentes demais ao mesmo tempo",
                "nada permanece claro por muito tempo",
                "a atenção se fragmenta fácil",
                "a mente não sustenta foco limpo",
                "tudo fica concorrendo junto"
            ],
            "probe": [
                "sua cabeça aquieta em algum momento do dia?",
                "isso fica te atravessando sem pausa?",
                "tem silêncio mental em algum trecho ou é quase contínuo?",
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
