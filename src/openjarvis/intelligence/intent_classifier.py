# src/openjarvis/intelligence/intent_classifier.py

from sentence_transformers import SentenceTransformer, util

class IntentClassifier:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.intents = {
            "open_app": [
                "abrir aplicativo",
                "abrir app",
                "launch app",
                "start application"
            ],
            "play_music": [
                "tocar música",
                "ouvir música",
                "play music"
            ],
        }

        self.intent_embeddings = {
            k: self.model.encode(v, convert_to_tensor=True)
            for k, v in self.intents.items()
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

        if best_score < 0.4:
            return "unknown"

        return best_intent
    
    def classify_with_confidence(self, text: str):
        intent = self.classify(text)
        confidence = 0.8  # TEMP (Melhorar Depois)
        return intent, confidence