from __future__ import annotations


class LenaHumanMemoryReflector:
    @staticmethod
    def emotional_recall(memory) -> str:
        topic = memory.social_state.current_topic

        if topic == "fatigue":
            return "você vem demonstrando um desgaste que não foi embora."

        if topic == "uncertainty":
            return "essa sensação de confusão mental tem aparecido repetidamente."

        if topic == "distress":
            return "essa pressão vem se repetindo mais do que um episódio solto."

        return "tem padrões emocionais se repetindo em você."

    @staticmethod
    def relational_reflection(memory) -> str:
        signature = memory.psychological_signature

        if signature == "fatigue_loop":
            return "eu te vejo tentando continuar até quando já está sem reserva."

        if signature == "uncertainty_loop":
            return "eu te vejo tentando achar clareza dentro de um pensamento embaralhado."

        if signature == "burnout_cognitive":
            return "eu te vejo exigindo funcionamento mesmo com a mente saturada."

        if signature == "distress_cycle":
            return "eu te vejo carregando mais peso interno do que descarrega."

        return "ainda estou formando uma leitura mais inteira de você."

    @staticmethod
    def self_summary(memory) -> str:
        pieces = []

        if "user_name" in memory.facts:
            pieces.append(f"teu nome é {memory.facts['user_name']}")

        if "location" in memory.facts:
            pieces.append(f"você mora em {memory.facts['location']}")

        if "study" in memory.facts:
            pieces.append(f"você cursa {memory.facts['study']}")

        signature = memory.psychological_signature

        if signature == "fatigue_loop":
            pieces.append("eu percebo um desgaste recorrente em você")
        elif signature == "uncertainty_loop":
            pieces.append("eu percebo uma busca frequente por clareza mental")
        elif signature == "burnout_cognitive":
            pieces.append("eu percebo uma mente funcionando sob saturação constante")
        elif signature == "distress_cycle":
            pieces.append("eu percebo um acúmulo emocional persistente")

        if memory.social_state.current_topic == "uncertainty":
            pieces.append("ultimamente você tem voltado muito para confusão e falta de encaixe")
        elif memory.social_state.current_topic == "fatigue":
            pieces.append("ultimamente o desgaste tem sido um tema recorrente")
        elif memory.social_state.current_topic == "distress":
            pieces.append("ultimamente a pressão interna tem reaparecido bastante")

        if not pieces:
            return "ainda em formação."

        return ". ".join(pieces) + "."
