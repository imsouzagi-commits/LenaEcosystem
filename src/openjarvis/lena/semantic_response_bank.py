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
                "tem uma sensação de desencontro aí dentro.",
                "alguma parte tua parece fora de encaixe.",
                "você não soa inteiro dentro do que tá vivendo.",
                "parece existir distância entre você e você mesmo."
            ],
            "subjective_effect": [
                "fica difícil se sentir no próprio lugar",
                "isso deixa tudo meio sem centro",
                "você vai ficando sem eixo",
                "nada encaixa por completo"
            ],
            "temporal_effect": [
                "isso continua voltando",
                "isso não recompõe sozinho",
                "mesmo quando passa um pouco isso retorna",
                "não some de verdade"
            ],
            "cognitive_effect": [
                "a cabeça tenta se localizar e não firma",
                "por dentro nada junta direito",
                "você tenta achar centro e não fixa",
                "as partes não fecham entre si"
            ],
            "probe": [
                "isso te acompanha mesmo em horas neutras?",
                "tem hora que você se sente deslocado sem motivo claro?"
            ],
        },

        "stagnation": {
            "anchor": [
                "tem uma sensação de movimento travado aí.",
                "alguma coisa tua ficou parada no mesmo ponto.",
                "isso não parece ganhar deslocamento.",
                "parece que internamente nada vira."
            ],
            "subjective_effect": [
                "vai dando cansaço de continuar no mesmo",
                "fica a impressão de rodar sem sair",
                "o mesmo ponto vai pesando",
                "isso começa a prender"
            ],
            "temporal_effect": [
                "e continua assim faz tempo",
                "o tempo passa e isso não mexe",
                "isso persiste mesmo depois de várias voltas",
                "não apareceu virada ainda"
            ],
            "cognitive_effect": [
                "a cabeça começa a parar de esperar mudança",
                "vai surgindo sensação de aprisionamento",
                "o raciocínio já espera que nada ande",
                "internamente parece ciclo repetido"
            ],
            "probe": [
                "você sente que sempre volta pro mesmo lugar?",
                "isso te dá sensação de aprisionamento?"
            ],
        },

        "clarity_seek": {
            "anchor": [
                "tem uma parte tua tentando entender isso.",
                "isso ainda não ficou claro por dentro.",
                "a tua mente continua procurando linha.",
                "parece faltar uma compreensão que feche."
            ],
            "subjective_effect": [
                "fica uma cobrança por entender",
                "isso não deixa a mente descansar",
                "a pergunta continua aberta",
                "não dá sensação de conclusão"
            ],
            "temporal_effect": [
                "isso reaparece toda hora",
                "mesmo quando você larga isso volta",
                "não some enquanto não entende",
                "continua internamente ativo"
            ],
            "cognitive_effect": [
                "a cabeça tenta organizar e não fecha",
                "o pensamento revisita isso sem parar",
                "a mente tenta costurar sentido",
                "você segue buscando uma linha"
            ],
            "probe": [
                "parece que enquanto não entende você não solta?",
                "isso continua pedindo explicação?"
            ],
        },

        "uncertainty": {
            "anchor": [
                "isso continua aberto aí dentro.",
                "alguma coisa nisso não fechou.",
                "isso ainda não assentou em você.",
                "permanece uma sensação de coisa inacabada."
            ],
            "subjective_effect": [
                "fica tudo meio pendurado",
                "isso não repousa",
                "permanece uma pendência",
                "nada termina por completo"
            ],
            "temporal_effect": [
                "e continua assim até agora",
                "o tempo passa e isso não encerra",
                "isso segue sem conclusão",
                "não fechou depois de várias voltas"
            ],
            "cognitive_effect": [
                "a cabeça tenta fechar e não consegue",
                "o pensamento roda atrás de encerramento",
                "internamente continua faltando uma peça",
                "isso não ganha conclusão mental"
            ],
            "probe": [
                "você sente que isso nunca fecha inteiro?",
                "mesmo quando tenta largar isso volta?"
            ],
        },

        "fatigue": {
            "anchor": [
                "isso tá te consumindo por dentro.",
                "tem um desgaste contínuo aí.",
                "você soa operando sem reposição.",
                "isso já virou cansaço acumulado."
            ],
            "subjective_effect": [
                "até o básico pesa mais",
                "qualquer coisa custa energia",
                "o mínimo já exige demais",
                "você funciona perto do limite"
            ],
            "temporal_effect": [
                "e não recompõe direito",
                "o descanso não devolve tudo",
                "isso vai se prolongando",
                "não zera entre um dia e outro"
            ],
            "cognitive_effect": [
                "até pensar exige esforço",
                "organizar coisas simples já custa",
                "a cabeça trabalha sem folga",
                "o mental opera cansado"
            ],
            "probe": [
                "você sente que para mas não recompõe?",
                "isso já tá virando cansaço contínuo?"
            ],
        },

        "mental_noise": {
            "anchor": [
                "tem ruído demais acontecendo na tua cabeça.",
                "a mente parece cheia o tempo todo.",
                "tá difícil achar faixa limpa aí dentro.",
                "existe turbulência mental contínua."
            ],
            "subjective_effect": [
                "os pensamentos se atropelam",
                "nada fica limpo por muito tempo",
                "fica difícil sustentar uma linha",
                "tudo concorre ao mesmo tempo"
            ],
            "temporal_effect": [
                "isso não abaixa por completo",
                "a cabeça segue ligada direto",
                "não entra calmaria consistente",
                "o ruído continua ativo"
            ],
            "cognitive_effect": [
                "o foco quebra fácil",
                "o pensamento não sustenta trilho",
                "a mente abre frente demais",
                "a atenção se fragmenta"
            ],
            "probe": [
                "isso te atravessa quase sem pausa?",
                "tem algum momento em que a cabeça aquieta?"
            ],
        },

        "neutral": {
            "anchor": [
                "tô acompanhando daqui",
                "continuo com você nessa",
                "sigo presente no que você trouxer",
                "te acompanho"
            ],
            "subjective_effect": [
                "o fio da conversa continua aberto",
                "a troca segue leve",
                "o contato continua correndo",
                "a conversa mantém presença"
            ],
            "temporal_effect": [
                "continuo aqui na sequência",
                "ainda tô te seguindo",
                "segue de onde quiser",
                "podemos continuar por essa linha"
            ],
            "cognitive_effect": [
                "vou mantendo isso em contexto",
                "consigo seguir o encadeamento",
                "tô dentro da mudança de assunto",
                "acompanho o próximo passo"
            ],
            "probe": [
                "quer puxar mais um pouco isso?",
                "pra onde você quer levar agora?"
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




    _SHADE_ROLE_BANK = {
        ("stagnation", "immobility"): {
            "anchor": [
                "isso continua parado no mesmo ponto.",
                "nada aí parece realmente deslocar.",
                "isso segue sem sair do lugar interno.",
            ],
            "subjective_effect": [
                "a sensação é de espera esvaziando.",
                "vai ficando difícil acreditar em mudança.",
                "internamente tudo parece suspenso.",
            ],
            "temporal_effect": [
                "o tempo passa e o cenário não mexe.",
                "as voltas passam e isso continua fixo.",
                "continua igual mesmo depois de insistir.",
            ],
            "cognitive_effect": [
                "a cabeça começa a desacreditar de virada.",
                "o raciocínio vai perdendo expectativa de avanço.",
                "vai se formando leitura de imobilidade.",
            ],
        },

        ("stagnation", "recurrence_loop"): {
            "anchor": [
                "isso continua voltando no mesmo circuito.",
                "a experiência gira e retorna pro mesmo ponto.",
                "tem repetição demais sem saída real.",
            ],
            "subjective_effect": [
                "a sensação é de ficar preso em loop.",
                "internamente parece rodar sem conclusão.",
                "isso dá impressão de retorno contínuo.",
            ],
            "temporal_effect": [
                "cada volta repete a anterior.",
                "o tempo anda mas o circuito reinicia.",
                "isso retorna mesmo depois de tentar soltar.",
            ],
            "cognitive_effect": [
                "a mente começa a ler isso como ciclo fechado.",
                "o raciocínio percebe repetição antes de mudança.",
                "vai ficando nítido o padrão circular.",
            ],
        },

        ("stagnation", "adhesive_hold"): {
            "anchor": [
                "isso não descola de dentro.",
                "alguma coisa aí continua aderida.",
                "isso segue preso sem aliviar.",
            ],
            "subjective_effect": [
                "a sensação é de retenção interna.",
                "parece que isso se agarra e não solta.",
                "fica um aprisionamento psíquico nisso.",
            ],
            "temporal_effect": [
                "mesmo com o passar das horas isso continua colado.",
                "o tempo não dissolve essa aderência.",
                "isso permanece grudado apesar das tentativas.",
            ],
            "cognitive_effect": [
                "a cabeça percebe que não tá conseguindo liberar.",
                "o raciocínio identifica retenção persistente.",
                "vai ficando claro que isso não circula, só prende.",
            ],
        },

        ("stagnation", "exhaustion"): {
            "anchor": [
                "isso já tá te consumindo por permanência.",
                "ficar nisso tá corroendo margem.",
                "a manutenção desse ponto já virou desgaste.",
            ],
            "subjective_effect": [
                "a sensação é de recurso interno baixando.",
                "vai faltando espaço pra sustentar isso.",
                "isso começa a virar exaustão de continuidade.",
            ],
            "temporal_effect": [
                "quanto mais permanece, mais drena.",
                "o tempo aqui não ajuda, só gasta.",
                "isso prolongado vai estreitando tua margem.",
            ],
            "cognitive_effect": [
                "a mente já lê isso como custo contínuo.",
                "o raciocínio percebe que a permanência tá cara.",
                "vai ficando evidente o desgaste por duração.",
            ],
        },

        ("fatigue", "depletion"): {
            "anchor": [
                "teu recurso interno tá baixando demais.",
                "isso tá te drenando quase por completo.",
                "a sustentação interna ficou curta.",
            ],
            "subjective_effect": [
                "parece que sobra muito pouco pra continuar.",
                "a sensação é de margem quase zerada.",
                "vai faltando reserva até pro mínimo.",
            ],
            "temporal_effect": [
                "quanto mais isso dura, menos resta.",
                "isso prolongado vai consumindo o que sobrou.",
                "o tempo aqui funciona como drenagem.",
            ],
            "cognitive_effect": [
                "a mente começa a operar em modo de escassez.",
                "o raciocínio percebe colapso de recurso.",
                "fica evidente que a sustentação tá no limite.",
            ],
        },

        ("fatigue", "basic_weight"): {
            "anchor": [
                "até o mínimo tá custando.",
                "coisas simples já vêm pesadas.",
                "o básico perdeu leveza interna.",
            ],
            "subjective_effect": [
                "qualquer movimento parece exigir demais.",
                "a sensação é de esforço acima do normal.",
                "tudo pede mais energia do que devia.",
            ],
            "temporal_effect": [
                "isso vai se repetindo ao longo do dia.",
                "não aparece faixa limpa de facilidade.",
                "mesmo tarefas pequenas continuam caras.",
            ],
            "cognitive_effect": [
                "a cabeça começa a contabilizar esforço em tudo.",
                "o mental lê excesso até no simples.",
                "fica nítido que não existe folga operacional.",
            ],
        },

        ("fatigue", "no_recovery"): {
            "anchor": [
                "o descanso não parece recompor.",
                "mesmo parando a energia não volta limpa.",
                "tem fadiga que continua depois da pausa.",
            ],
            "subjective_effect": [
                "a sensação é de não resetar.",
                "parece que o corpo não recompõe direito.",
                "internamente continua um fundo de cansaço.",
            ],
            "temporal_effect": [
                "você para e isso continua junto.",
                "as horas passam sem recuperação real.",
                "nem depois de dormir parece zerar.",
            ],
            "cognitive_effect": [
                "a cabeça começa a entender que não é só esforço pontual.",
                "o raciocínio já lê falha de recomposição.",
                "isso toma forma de fadiga persistente.",
            ],
        },

        ("mental_noise", "no_quiet"): {
            "anchor": [
                "a mente não consegue baixar.",
                "não aparece faixa interna de sossego.",
                "isso continua sem aquietar por dentro.",
            ],
            "subjective_effect": [
                "a sensação é de agitação contínua.",
                "parece impossível gerar silêncio mental.",
                "fica um ruído que não desce.",
            ],
            "temporal_effect": [
                "o tempo passa e a cabeça continua ativa.",
                "mesmo tentando pausar isso não abaixa.",
                "não entra descanso mental mesmo com intervalo.",
            ],
            "cognitive_effect": [
                "o raciocínio percebe ausência de quietude.",
                "a mente começa a cansar de não reduzir.",
                "fica evidente que não há desaceleração interna.",
            ],
        },
    }

    @staticmethod
    def role_anchor(topic: str, shade: str | None = None) -> list[str]:
        if shade and (topic, shade) in LenaSemanticResponseBank._SHADE_ROLE_BANK:
            return LenaSemanticResponseBank._SHADE_ROLE_BANK[(topic, shade)]["anchor"]
        return LenaSemanticResponseBank._ROLE_BANK.get(topic, LenaSemanticResponseBank._ROLE_BANK["uncertainty"])["anchor"]

    @staticmethod
    def role_subjective(topic: str, shade: str | None = None) -> list[str]:
        if shade and (topic, shade) in LenaSemanticResponseBank._SHADE_ROLE_BANK:
            return LenaSemanticResponseBank._SHADE_ROLE_BANK[(topic, shade)]["subjective_effect"]
        return LenaSemanticResponseBank._ROLE_BANK.get(topic, LenaSemanticResponseBank._ROLE_BANK["uncertainty"])["subjective_effect"]

    @staticmethod
    def role_temporal(topic: str, shade: str | None = None) -> list[str]:
        if shade and (topic, shade) in LenaSemanticResponseBank._SHADE_ROLE_BANK:
            return LenaSemanticResponseBank._SHADE_ROLE_BANK[(topic, shade)]["temporal_effect"]
        return LenaSemanticResponseBank._ROLE_BANK.get(topic, LenaSemanticResponseBank._ROLE_BANK["uncertainty"])["temporal_effect"]

    @staticmethod
    def role_cognitive(topic: str, shade: str | None = None) -> list[str]:
        if shade and (topic, shade) in LenaSemanticResponseBank._SHADE_ROLE_BANK:
            return LenaSemanticResponseBank._SHADE_ROLE_BANK[(topic, shade)]["cognitive_effect"]
        return LenaSemanticResponseBank._ROLE_BANK.get(topic, LenaSemanticResponseBank._ROLE_BANK["uncertainty"])["cognitive_effect"]

    @staticmethod
    def role_probe(topic: str) -> list[str]:
        return LenaSemanticResponseBank._ROLE_BANK.get(topic, LenaSemanticResponseBank._ROLE_BANK["uncertainty"])["probe"]


    @staticmethod
    def soften(memory, text: str) -> str:
        return " ".join(text.strip().split())
