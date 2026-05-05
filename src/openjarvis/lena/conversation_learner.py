from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from openjarvis.lena.boot_logger import LenaBootLogger
from openjarvis.lena.learned_patterns import LenaLearnedPatterns
from openjarvis.lena.learned_responses import LenaLearnedResponses


class LenaConversationLearner:
    VALID_TOPICS = {"fatigue", "uncertainty", "distress", "overload", "frustration", "mental_noise", "disconnection", "stagnation", "clarity_seek"}

    @staticmethod
    def _sanitize_raw(raw: str) -> str:
        if not raw:
            return ""

        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL | re.IGNORECASE)
        raw = raw.replace("```json", "").replace("```", "")
        raw = raw.replace("\u201c", '"').replace("\u201d", '"')
        return raw.strip()

    @classmethod
    def _extract_json(cls, raw: str) -> Optional[Dict[str, Any]]:
        raw = cls._sanitize_raw(raw)
        if not raw:
            return None

        candidates = re.findall(r"\{.*?\}", raw, re.DOTALL)

        for chunk in reversed(candidates):
            try:
                data = json.loads(chunk)
                if isinstance(data, dict):
                    return data
            except Exception:
                continue

        return None

    @staticmethod
    def _fallback_topic(user_text: str) -> str:
        lowered = user_text.lower()

        if any(x in lowered for x in ("cansado", "exausto", "sem energia", "desanimado")):
            return "fatigue"

        if any(x in lowered for x in ("ansioso", "ansiosa", "sobrecarregado", "sobrecarregada", "mal", "pesado")):
            return "distress"

        if any(x in lowered for x in ("coisa demais", "tudo junto", "muita coisa", "atolado")):
            return "overload"

        if any(x in lowered for x in ("travado", "travada", "na mesma", "frustrante")):
            return "frustration"

        if any(x in lowered for x in ("ruido mental", "mente rodando", "pensamento demais")):
            return "mental_noise"

        if any(x in lowered for x in ("nada encaixa", "desconexo", "nada conecta")):
            return "disconnection"

        if any(x in lowered for x in ("estagnado", "estagnada", "preso nisso", "parado")):
            return "stagnation"

        if any(x in lowered for x in ("preciso entender", "quero clareza", "preciso organizar")):
            return "clarity_seek"

        if any(x in lowered for x in ("confuso", "confusa", "não sei", "nao sei", "embaralhado", "embaralhada")):
            return "uncertainty"

        return "none"

    @staticmethod
    def _fallback_markers(user_text: str) -> List[str]:
        lowered = user_text.lower().strip()
        parts = re.split(r"[,.!?;]| mas | porque | que ", lowered)
        markers = []

        for part in parts:
            cleaned = part.strip()
            if 5 <= len(cleaned) <= 40:
                markers.append(cleaned)

        return markers[:3]

    @staticmethod
    def _fallback_responses(topic: str) -> List[str]:
        if topic == "fatigue":
            return [
                "isso tá com cara de desgaste acumulado.",
                "você não anda descansando por dentro.",
                "tem um peso aí que não soltou.",
            ]

        if topic == "uncertainty":
            return [
                "isso tá com cara de névoa mental.",
                "teu pensamento não tá encaixando direito.",
                "tem ruído demais passando aí dentro.",
            ]

        if topic == "distress":
            return [
                "isso tá te pressionando mais do que parece.",
                "tem coisa demais em cima de você.",
                "isso não tá leve dentro.",
            ]

        return []

    @staticmethod
    def build_learning_prompt(user_text: str) -> str:
        return f"""
Classifique semanticamente a frase humana abaixo.

Frase: "{user_text}"

Responda SOMENTE JSON válido:
{{
  "topic": "fatigue, uncertainty, distress, overload, frustration, mental_noise, disconnection, stagnation, clarity_seek ou none",
  "markers": ["até 3 marcadores curtos"],
  "responses": ["3 respostas humanas curtas em português"]
}}
""".strip()

    @classmethod
    def _query_llm(cls, agent, prompt: str) -> str:
        raw = ""

        try:
            if agent.smart_brain.azure_engine.available:
                raw = agent.smart_brain.azure_engine.complete(
                    [
                        {"role": "system", "content": "Você é um extrator semântico e responde apenas JSON válido."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                    max_tokens=120,
                    timeout=3.0,
                )
        except Exception as exc:
            LenaBootLogger.write(f"conversation learner azure fail: {exc}")

        if raw:
            return raw

        try:
            if agent.smart_brain.ollama_engine.available:
                raw = agent.smart_brain.ollama_engine.complete(
                    prompt,
                    reflective=False,
                    temperature=0.1,
                    max_tokens=120,
                )
        except Exception as exc:
            LenaBootLogger.write(f"conversation learner ollama fail: {exc}")

        return raw

    @classmethod
    def learn(cls, agent, user_text: str) -> bool:
        prompt = cls.build_learning_prompt(user_text)
        raw = cls._query_llm(agent, prompt)

        LenaBootLogger.write(f"conversation learner raw: {repr(raw)}")

        data = cls._extract_json(raw)

        if data:
            topic = str(data.get("topic", "")).strip().lower()
            markers = list(data.get("markers", []))
            responses = list(data.get("responses", []))
        else:
            topic = cls._fallback_topic(user_text)
            markers = cls._fallback_markers(user_text)
            responses = cls._fallback_responses(topic)

        LenaBootLogger.write(
            f"conversation learner parsed: topic={topic} markers={markers} responses={len(responses)}"
        )

        if topic not in cls.VALID_TOPICS:
            return False

        LenaLearnedPatterns.add_markers(topic, markers)
        LenaLearnedResponses.add_responses(topic, responses)
        return True
