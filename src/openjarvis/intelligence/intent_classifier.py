from sentence_transformers import SentenceTransformer, util


class IntentClassifier:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.intents = {
            "open": [
                "abrir aplicativo",
                "abrir app",
                "abre spotify",
                "abre safari",
                "launch application",
                "open app"
            ],
            "close": [
                "fechar aplicativo",
                "fecha spotify",
                "close app",
                "quit application"
            ],
            "up": [
                "aumentar volume",
                "sobe o som",
                "increase volume",
                "turn volume up"
            ],
            "down": [
                "abaixar volume",
                "diminuir som",
                "decrease volume",
                "turn volume down"
            ],
            "on": [
                "ligar wifi",
                "ativar wifi",
                "turn wifi on"
            ],
            "off": [
                "desligar wifi",
                "desativar wifi",
                "turn wifi off"
            ],
            "play_music": [
                "tocar música",
                "ouvir música",
                "play music"
            ],
        }

        self.intent_embeddings = {
            key: self.model.encode(samples, convert_to_tensor=True)
            for key, samples in self.intents.items()
        }

    def classify(self, query: str) -> str:
        query_emb = self.model.encode(query, convert_to_tensor=True)

        best_intent = "unknown"
        best_score = 0.0

        for intent, emb in self.intent_embeddings.items():
            score = util.cos_sim(query_emb, emb).max().item()

            if score > best_score:
                best_score = score
                best_intent = intent

        if best_score < 0.38:
            return "unknown"

        return best_intent

    def classify_with_confidence(self, text: str):
        query_emb = self.model.encode(text, convert_to_tensor=True)

        best_intent = "unknown"
        best_score = 0.0

        for intent, emb in self.intent_embeddings.items():
            score = util.cos_sim(query_emb, emb).max().item()

            if score > best_score:
                best_score = score
                best_intent = intent

        if best_score < 0.38:
            return "unknown", best_score

        return best_intent, best_score