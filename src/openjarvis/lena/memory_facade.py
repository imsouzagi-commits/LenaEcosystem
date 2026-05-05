from __future__ import annotations

from dataclasses import fields
import time
import threading
from typing import Any, Dict, List, Tuple

from openjarvis.lena.boot_logger import LenaBootLogger
from openjarvis.lena.learned_patterns import LenaLearnedPatterns
from openjarvis.lena.learned_responses import LenaLearnedResponses
from openjarvis.lena.relational_impression import LenaRelationalImpression
from openjarvis.lena.human_memory_reflector import LenaHumanMemoryReflector
from openjarvis.lena.memory_persistence import LenaMemoryPersistence
from openjarvis.lena.social_state import LenaSocialState
from openjarvis.lena.continuity_engine import LenaContinuityEngine
from openjarvis.lena.response_selector import LenaResponseSelector
from openjarvis.lena.narrative_tension_engine import LenaNarrativeTensionEngine
from openjarvis.lena.intention_memory_engine import LenaIntentionMemoryEngine
from openjarvis.lena.closure_cognition_engine import LenaClosureCognitionEngine
from openjarvis.lena.learning_runtime import LenaLearningRuntime


class LenaMemoryFacade:
    MAX_HISTORY_HEAVY = 120
    MAX_HISTORY_LIGHT = 40
    MAX_SEMANTIC_SNIPPETS = 12
    MAX_EPISODIC_EVENTS = 40

    OPERATIONAL_ROUTES = {
        "DESKTOP",
        "FILE_OP",
        "WEB_OPEN",
        "WEB_SEARCH",
        "LENA_STATUS",
        "LENA_PAGE",
        "TASK_CHAIN_HYBRID",
    }

    NON_EVOLVING_ROUTES = {
        "MEMORY",
    }

    def __init__(self) -> None:
        payload = LenaMemoryPersistence.load()
        LenaBootLogger.write("Lena persistent memory loaded")
        self._lock = threading.RLock()

        self.schema_version = int(payload.get("schema_version", LenaMemoryPersistence.SCHEMA_VERSION))
        self.state: Dict[str, Any] = dict(payload.get("state", {}))
        self.history: List[Tuple[str, str]] = self._restore_history(payload.get("history"))
        self.facts: Dict[str, str] = dict(payload.get("facts", {}))
        self.emotional_history: List[str] = list(payload.get("emotional_history", []))
        self.topic_counters: Dict[str, int] = dict(payload.get("topic_counters", {}))
        self.semantic_emotional_snippets: List[str] = list(payload.get("semantic_emotional_snippets", []))
        self.psychological_signature: str = str(payload.get("psychological_signature", "stable"))
        self.psychological_profile: List[str] = list(payload.get("psychological_profile", []))
        self.episodic_events: List[Dict[str, Any]] = self._restore_episodic_events(payload.get("episodic_events"))
        self.recent_topic_windows: Dict[str, int] = {}
        self.semantic_response_history: Dict[str, List[str]] = {}
        self.exchange_significance: int = int(payload.get("exchange_significance", 0))
        self.social_state: LenaSocialState = LenaSocialState(session_boot_id=int(time.time()))
        self.narrative_state = LenaNarrativeTensionEngine.restore({})
        self.intention_state = LenaIntentionMemoryEngine.restore({})

        LenaLearningRuntime.reload_semantic_banks(self)

    def _restore_history(self, value: Any) -> List[Tuple[str, str]]:
        if not isinstance(value, list):
            return []
        out: List[Tuple[str, str]] = []
        for item in value:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                out.append((str(item[0]), str(item[1])))
        return out[-self.MAX_HISTORY_HEAVY:]

    def _restore_episodic_events(self, value: Any) -> List[Dict[str, Any]]:
        if not isinstance(value, list):
            return []
        out: List[Dict[str, Any]] = []
        for item in value:
            if isinstance(item, dict):
                out.append(
                    {
                        "text": str(item.get("text", "")),
                        "semantic_topic": str(item.get("semantic_topic", "")),
                        "route": str(item.get("route", "")),
                        "ts": float(item.get("ts", time.time())),
                    }
                )
        return out[-self.MAX_EPISODIC_EVENTS:]

    def _restore_social_state(self, value: Any) -> LenaSocialState:
        if not isinstance(value, dict):
            return LenaSocialState(session_boot_id=int(time.time()))

        valid_fields = {field.name for field in fields(LenaSocialState)}
        filtered = {k: v for k, v in value.items() if k in valid_fields}
        filtered.setdefault("session_boot_id", int(time.time()))

        try:
            return LenaSocialState(**filtered)
        except Exception:
            return LenaSocialState(session_boot_id=int(time.time()))

    def recent_dialogue_context(self, limit: int = 6) -> str:
        if not self.history:
            return "sem histórico"

        parts: List[str] = []
        for user_text, assistant_text in self.history[-limit:]:
            parts.append(f"U:{user_text}")
            parts.append(f"L:{assistant_text}")
        return " | ".join(parts)

    def push_exchange(self, user_text: str, assistant_text: str, light: bool = False, route_used: str = "") -> None:
        with self._lock:
            self.history.append((user_text, assistant_text))
            self.history = self.history[-(self.MAX_HISTORY_LIGHT if light else self.MAX_HISTORY_HEAVY):]

            LenaLearningRuntime.reload_semantic_banks(self)
            LenaNarrativeTensionEngine.ingest_assistant(self, assistant_text)
            self._persist()

    def ingest_user_turn(self, user_text: str, route_used: str = "") -> None:
        with self._lock:
            self._extract_facts(user_text)

            if route_used not in self.OPERATIONAL_ROUTES and route_used not in self.NON_EVOLVING_ROUTES:
                lowered = user_text.lower().strip()
                personal_only = lowered.startswith(("meu nome é ", "eu moro em ", "curso ", "estou construindo "))

                if not personal_only:
                    self._evolve_social_state(user_text)
                    LenaClosureCognitionEngine.ingest(self, user_text)
                    LenaNarrativeTensionEngine.ingest_user(self, user_text, self._contextual_semantic_topic(user_text.lower()))
                    self._capture_episodic_event(user_text, route_used)

    def _persist(self) -> None:
        try:
            LenaMemoryPersistence.save(
                {
                    "schema_version": LenaMemoryPersistence.SCHEMA_VERSION,
                    "state": self.state,
                    "history": self.history,
                    "facts": self.facts,
                    "emotional_history": self.emotional_history,
                    "topic_counters": self.topic_counters,
                    "semantic_emotional_snippets": self.semantic_emotional_snippets,
                    "psychological_signature": self.psychological_signature,
                    "psychological_profile": self.psychological_profile,
                    "episodic_events": self.episodic_events,
                    "recent_topic_windows": self.recent_topic_windows,
                    "semantic_response_history": self.semantic_response_history,
                    "exchange_significance": self.exchange_significance,
                    "social_state": dict(self.social_state.__dict__),
                    "narrative_state": LenaNarrativeTensionEngine.export(self.narrative_state),
                    "intention_state": LenaIntentionMemoryEngine.export(self.intention_state),
                }
            )
        except Exception as exc:
            LenaBootLogger.write(f"memory facade persistence failed: {exc}")

    def _extract_facts(self, user_text: str) -> None:
        lowered = user_text.lower().strip()

        if lowered.startswith("meu nome é "):
            self.facts["user_name"] = user_text[10:].strip()

        if lowered.startswith("eu moro em "):
            self.facts["location"] = user_text[10:].strip()

        if lowered.startswith("curso "):
            self.facts["study"] = user_text[6:].strip()


    def needs_learning(self, lowered: str) -> bool:
        emotional_hints = (
            "acho que",
            "me sinto",
            "sinto que",
            "minha cabeça",
            "não tô",
            "nao to",
            "tô meio",
            "to meio",
            "ultimamente",
            "não sei se",
            "nao sei se",
        )
        if not any(hint in lowered for hint in emotional_hints):
            return False
        return self._semantic_emotion_topic(lowered) is None

    def _detect_user_intent(self, lowered: str) -> str:
        if any(x in lowered for x in (
            "qual meu nome",
            "faz um resumo",
            "tudo que você sabe",
            "o que você acha de mim",
            "me lembra como eu estou me sentindo",
            "quem sou eu até agora",
        )):
            return "memory_probe"

        return "neutral"

    def _memory_probe_type(self, lowered: str) -> str:
        if "qual meu nome" in lowered:
            return "factual_name"
        if "onde eu moro" in lowered or "eu moro onde" in lowered:
            return "factual_location"
        if "qual meu curso" in lowered or "o que eu curso" in lowered:
            return "factual_study"
        if "como eu estou me sentindo" in lowered or "me lembra como eu estou me sentindo" in lowered:
            return "emotional_recall"
        if "o que você acha de mim" in lowered or "o que voce acha de mim" in lowered or "como você me vê" in lowered:
            return "relational_reflection"
        if "quem sou eu até agora" in lowered or "faz um resumo" in lowered or "tudo que você sabe de mim" in lowered:
            return "self_summary"
        return "generic"

    def answer_memory_question(self, lowered: str) -> str:
        probe = self._memory_probe_type(lowered)

        if probe == "factual_name":
            return f"teu nome ficou comigo, {self.facts['user_name']}." if "user_name" in self.facts else "ainda não."

        if probe == "factual_location":
            return f"você mora em {self.facts['location']}." if "location" in self.facts else "ainda não."

        if probe == "factual_study":
            return f"você cursa {self.facts['study']}." if "study" in self.facts else "ainda não."

        if probe == "emotional_recall":
            return LenaHumanMemoryReflector.emotional_recall(self)

        if probe == "relational_reflection":
            impression = LenaRelationalImpression.infer(self)
            return impression if impression else LenaHumanMemoryReflector.relational_reflection(self)

        if probe == "self_summary":
            return LenaHumanMemoryReflector.self_summary(self)

        return "fragmentos ainda."

    def live_emotional_read(self, lowered: str) -> str:
        topic = self._contextual_semantic_topic(lowered)
        continuity = LenaContinuityEngine.resolve(self, topic)

        if continuity["topic"]:
            return LenaResponseSelector.choose(self, continuity["topic"], continuity["stage"], "mirror")

        return "eu percebo alguma coisa desalinhada nisso."

    def last_semantic_emotional_snippets(self, limit: int = 2) -> List[str]:
        return self.semantic_emotional_snippets[-limit:]

    def emotional_topic_recurrence(self, topic: str) -> int:
        return int(self.topic_counters.get(topic, 0))

    def remember_semantic_response(self, topic: str, text: str) -> None:
        bucket = list(self.semantic_response_history.get(topic, []))
        bucket.append(text)
        self.semantic_response_history[topic] = bucket[-3:]

    def recent_semantic_responses(self, topic: str) -> List[str]:
        return list(self.semantic_response_history.get(topic, []))


    def remember_semantic_fragment(self, fragment: str) -> None:
        if not fragment:
            return
        bucket = list(self.semantic_response_history.get("__fragments__", []))
        bucket.append(fragment.strip().lower())
        self.semantic_response_history["__fragments__"] = bucket[-12:]

    def recent_semantic_fragments(self) -> List[str]:
        return list(self.semantic_response_history.get("__fragments__", []))

    def remember_syntax_family(self, family: str) -> None:
        if not family:
            return
        bucket = list(self.semantic_response_history.get("__syntax__", []))
        bucket.append(family)
        self.semantic_response_history["__syntax__"] = bucket[-8:]

    def recent_syntax_families(self) -> List[str]:
        return list(self.semantic_response_history.get("__syntax__", []))

    def infer_psychological_signature(self) -> str:
        fatigue = self.emotional_topic_recurrence("fatigue")
        uncertainty = self.emotional_topic_recurrence("uncertainty")
        distress = self.emotional_topic_recurrence("distress")

        profile: List[str] = []
        if fatigue >= 2:
            profile.append("fatigue_loop")
        if uncertainty >= 2:
            profile.append("uncertainty_loop")
        if distress >= 2:
            profile.append("distress_cycle")
        if fatigue >= 2 and uncertainty >= 2:
            profile.append("burnout_cognitive")

        if not profile:
            profile = ["stable"]

        self.psychological_profile = profile
        self.psychological_signature = "burnout_cognitive" if "burnout_cognitive" in profile else profile[0]
        return self.psychological_signature

    
    def _estimate_exchange_significance(self, user_text: str) -> int:
        lowered = user_text.lower()

        score = 0

        semantic_topic = self._contextual_semantic_topic(lowered)
        if semantic_topic:
            score += 2

        if any(x in lowered for x in (
            "continua", "ainda", "mesmo", "de novo", "segue", "de novo nisso",
            "qual meu nome", "você lembra", "voce lembra", "o que eu falei",
        )):
            score += 2

        if len(user_text.split()) >= 8:
            score += 1

        if self.narrative_state.unresolved_user_threads or self.narrative_state.assistant_open_loops:
            score += 1

        if self.intention_state.open_intentions:
            score += 1

        return min(score, 6)


    def _capture_episodic_event(self, user_text: str, route_used: str) -> None:
        significance = self._estimate_exchange_significance(user_text)
        self.exchange_significance += significance

        if significance <= 0:
            return

        self.episodic_events.append(
            {
                "text": user_text.strip(),
                "semantic_topic": self._contextual_semantic_topic(user_text.lower()) or "",
                "route": route_used,
                "ts": time.time(),
            }
        )
        self.episodic_events = self.episodic_events[-self.MAX_EPISODIC_EVENTS:]

    
    def _evolve_social_state(self, user_text: str) -> None:
        lowered = user_text.lower().strip()
        detected_topic = self._contextual_semantic_topic(lowered)
        lexical_topic = self._semantic_emotion_topic(lowered)
        social = self.social_state

        social.turns_count += 1
        word_count = len(user_text.split())

        continuity_markers = (
            "continua", "ainda", "de novo", "mesmo", "igual", "segue",
            "não acabou", "nao acabou", "permanece", "ainda tá", "ainda ta",
            "você lembra", "voce lembra", "qual meu nome", "o que eu falei",
        )
        explicit_continuity = any(marker in lowered for marker in continuity_markers)

        live_narrative = bool(self.narrative_state.unresolved_user_threads or self.narrative_state.assistant_open_loops)
        live_intentions = bool(self.intention_state.open_intentions)
        reflective_question = lowered.endswith("?") and word_count >= 4
        meaningful_turn = bool(
            detected_topic
            or lexical_topic
            or explicit_continuity
            or reflective_question
        )

        def rise(value: int, amount: int = 1, cap: int = 10) -> int:
            return min(cap, value + amount)

        def decay(value: int, amount: int = 1) -> int:
            return max(0, value - amount)

        if detected_topic:
            previous_window = self.recent_topic_windows.get(detected_topic, 0)
            self.topic_counters[detected_topic] = self.topic_counters.get(detected_topic, 0) + 1
            self.recent_topic_windows[detected_topic] = min(10, previous_window + 2)
            self.semantic_emotional_snippets.append(user_text.strip())
            self.semantic_emotional_snippets = self.semantic_emotional_snippets[-self.MAX_SEMANTIC_SNIPPETS:]
            social.current_topic = detected_topic
            social.last_emotion_topic = detected_topic
        else:
            previous_window = 0
            dominant_window = self.recent_topic_windows.get(social.current_topic, 0)
            if dominant_window <= 1:
                social.current_topic = "neutral"

        for key in list(self.recent_topic_windows.keys()):
            if key != social.current_topic:
                self.recent_topic_windows[key] = max(0, self.recent_topic_windows.get(key, 0) - 1)

        if meaningful_turn:
            social.familiarity = rise(social.familiarity, 1)
            social.presence_momentum = rise(social.presence_momentum, 1)

        if meaningful_turn and (word_count >= 4 or lowered.endswith("?")):
            social.trust_level = rise(social.trust_level, 1)

        if meaningful_turn and social.turns_count >= 4:
            social.conversation_depth = rise(social.conversation_depth, 1)

        if explicit_continuity:
            social.unresolved_loops = rise(social.unresolved_loops, 1)
            social.emotional_tension = rise(social.emotional_tension, 1)
        elif live_narrative or live_intentions:
            social.unresolved_loops = rise(social.unresolved_loops, 1 if word_count >= 6 else 0)
            social.emotional_tension = rise(social.emotional_tension, 1 if detected_topic else 0)

        if detected_topic and (explicit_continuity or previous_window >= 3):
            social.emotional_gravity = rise(social.emotional_gravity, 1)

        if social.trust_level >= 4 and social.unresolved_loops >= 3:
            social.reflection_depth = rise(social.reflection_depth, 1)

        if social.reflection_depth >= 3:
            social.intimacy_level = rise(social.intimacy_level, 1)

        if social.intimacy_level >= 2:
            social.warmth_level = rise(social.warmth_level, 1)

        if not meaningful_turn:
            social.presence_momentum = decay(social.presence_momentum, 1)

        if not explicit_continuity and not live_narrative and not live_intentions and not detected_topic:
            social.unresolved_loops = decay(social.unresolved_loops, 1)
            social.emotional_tension = decay(social.emotional_tension, 1)

        if social.unresolved_loops >= 5:
            social.current_conversation_arc = "deepening"
        elif social.unresolved_loops >= 2:
            social.current_conversation_arc = "holding"
        else:
            social.current_conversation_arc = "surface"

        social.arc_stage = min(
            10,
            int(
                social.conversation_depth * 0.35 +
                social.trust_level * 0.20 +
                social.reflection_depth * 0.20 +
                social.presence_momentum * 0.15 +
                social.unresolved_loops * 0.10
            )
        )

        active_topics = [v for v in self.recent_topic_windows.values() if v > 0]
        social.continuity_score = min(10, len(active_topics))

        self.infer_psychological_signature()


    def _semantic_topic_scores(self, lowered: str) -> dict[str, float]:
        normalized = lowered.lower().strip()

        weighted_roots = {
            "disconnection": {
                "tem algo desconectado": 4, "desconect": 3, "fora do lugar": 4, "fora do eixo": 4,
                "não consigo me achar": 5, "nao consigo me achar": 5, "não consigo me encontrar": 5, "nao consigo me encontrar": 5,
                "sem encaixe": 4, "não caber": 3, "nao caber": 3, "fora do eixo": 4, "desalinhado": 4, "não me localizo": 4, "nao me localizo": 4, "nao caber": 3, "desencontrado": 4, "me prendendo": 3, "não me encontro": 5, "nao me encontro": 5,
            },
            "stagnation": {
                "nada anda": 5, "preso nisso": 5, "travado": 4, "mesmo ponto": 4, "não saio": 3, "nao saio": 3,
                "continua igual": 3, "sem sair disso": 4, "sem deslocamento": 3, "parado": 3, "não anda": 4,
            },
            "clarity_seek": {
                "não consigo entender": 5, "nao consigo entender": 5, "preciso organizar": 4, "linha sobre isso": 4,
                "não faz sentido": 4, "nao faz sentido": 4, "clareza": 3, "estruturar isso": 4, "montar sentido": 3, "organizar minha cabeça": 5, "não monto linha": 5, "nao monto linha": 5, "não consigo organizar": 5, "nao consigo organizar": 5, "tento estruturar": 4,
            },
            "uncertainty": {
                "em aberto": 5, "aberto ainda": 5, "não fecha": 5, "nao fecha": 5, "pendurado em mim": 5,
                "sem conclusão": 5, "inacabado": 4, "continua me rondando": 4, "fechamento": 3, "encerramento": 3,
            },
            "fatigue": {
                "drenado": 5, "sem margem": 4, "desgaste acumulado": 5, "não recomponho": 5, "nao recomponho": 5,
                "sem energia": 4, "exausto": 4, "funcionando sem energia": 5, "sem reposição": 3, "cansado": 3, "não volto": 5, "nao volto": 5, "não recompõe": 5, "nao recompõe": 5, "bateria nunca enche": 5, "vou drenando": 4, "só dreno": 4, "sem força": 4,
            },
            "mental_noise": {
                "ruído": 5, "ruido": 5, "cabeça não aquieta": 5, "cabeca não aquieta": 5, "cabeca nao aquieta": 5,
                "pensamento demais": 5, "penso demais": 5, "barulho demais": 5, "mente acelerada": 5, "mente corre": 5, "não desligo": 4, "nao desligo": 4, "sem foco": 4, "embaralhado": 4, "silêncio mental": 5, "silencio mental": 5,
                "não encontro silêncio": 5, "nao encontro silencio": 5, "mente não para": 4, "mente nao para": 4,
            },
        }

        scores = {}

        for topic, roots in weighted_roots.items():
            topic_score = 0.0

            for root, weight in roots.items():
                if root in normalized:
                    topic_score += weight

            if self._matches_learned_topic(normalized, topic):
                topic_score += 2.0

            topic_score += min(0.35, self.recent_topic_windows.get(topic, 0) * 0.05)

            if self.social_state.current_topic == topic and self._is_contextual_continuation(normalized):
                topic_score += 0.18

            if topic_score > 0:
                scores[topic] = topic_score

        return scores



    def _capture_episodic_event(self, user_text: str, route_used: str) -> None:
        significance = self._estimate_exchange_significance(user_text)
        self.exchange_significance += significance

        if significance <= 0:
            return

        self.episodic_events.append(
            {
                "text": user_text.strip(),
                "semantic_topic": self._contextual_semantic_topic(user_text.lower()) or "",
                "route": route_used,
                "ts": time.time(),
            }
        )
        self.episodic_events = self.episodic_events[-self.MAX_EPISODIC_EVENTS:]

    
    def _evolve_social_state(self, user_text: str) -> None:
        lowered = user_text.lower().strip()
        detected_topic = self._contextual_semantic_topic(lowered)
        lexical_topic = self._semantic_emotion_topic(lowered)
        social = self.social_state

        social.turns_count += 1
        word_count = len(user_text.split())

        continuity_markers = (
            "continua", "ainda", "de novo", "mesmo", "igual", "segue",
            "não acabou", "nao acabou", "permanece", "ainda tá", "ainda ta",
            "você lembra", "voce lembra", "qual meu nome", "o que eu falei",
        )
        explicit_continuity = any(marker in lowered for marker in continuity_markers)

        live_narrative = bool(self.narrative_state.unresolved_user_threads or self.narrative_state.assistant_open_loops)
        live_intentions = bool(self.intention_state.open_intentions)
        reflective_question = lowered.endswith("?") and word_count >= 4
        meaningful_turn = bool(
            detected_topic
            or lexical_topic
            or explicit_continuity
            or reflective_question
        )

        def rise(value: int, amount: int = 1, cap: int = 10) -> int:
            return min(cap, value + amount)

        def decay(value: int, amount: int = 1) -> int:
            return max(0, value - amount)

        if detected_topic:
            previous_window = self.recent_topic_windows.get(detected_topic, 0)
            self.topic_counters[detected_topic] = self.topic_counters.get(detected_topic, 0) + 1
            self.recent_topic_windows[detected_topic] = min(10, previous_window + 2)
            self.semantic_emotional_snippets.append(user_text.strip())
            self.semantic_emotional_snippets = self.semantic_emotional_snippets[-self.MAX_SEMANTIC_SNIPPETS:]
            social.current_topic = detected_topic
            social.last_emotion_topic = detected_topic
        else:
            previous_window = 0
            dominant_window = self.recent_topic_windows.get(social.current_topic, 0)
            if dominant_window <= 1:
                social.current_topic = "neutral"

        for key in list(self.recent_topic_windows.keys()):
            if key != social.current_topic:
                self.recent_topic_windows[key] = max(0, self.recent_topic_windows.get(key, 0) - 1)

        if meaningful_turn:
            social.familiarity = rise(social.familiarity, 1)
            social.presence_momentum = rise(social.presence_momentum, 1)

        if meaningful_turn and (word_count >= 4 or lowered.endswith("?")):
            social.trust_level = rise(social.trust_level, 1)

        if meaningful_turn and social.turns_count >= 4:
            social.conversation_depth = rise(social.conversation_depth, 1)

        if explicit_continuity:
            social.unresolved_loops = rise(social.unresolved_loops, 1)
            social.emotional_tension = rise(social.emotional_tension, 1)
        elif live_narrative or live_intentions:
            social.unresolved_loops = rise(social.unresolved_loops, 1 if word_count >= 6 else 0)
            social.emotional_tension = rise(social.emotional_tension, 1 if detected_topic else 0)

        if detected_topic and (explicit_continuity or previous_window >= 3):
            social.emotional_gravity = rise(social.emotional_gravity, 1)

        if social.trust_level >= 4 and social.unresolved_loops >= 3:
            social.reflection_depth = rise(social.reflection_depth, 1)

        if social.reflection_depth >= 3:
            social.intimacy_level = rise(social.intimacy_level, 1)

        if social.intimacy_level >= 2:
            social.warmth_level = rise(social.warmth_level, 1)

        if not meaningful_turn:
            social.presence_momentum = decay(social.presence_momentum, 1)

        if not explicit_continuity and not live_narrative and not live_intentions and not detected_topic:
            social.unresolved_loops = decay(social.unresolved_loops, 1)
            social.emotional_tension = decay(social.emotional_tension, 1)

        if social.unresolved_loops >= 5:
            social.current_conversation_arc = "deepening"
        elif social.unresolved_loops >= 2:
            social.current_conversation_arc = "holding"
        else:
            social.current_conversation_arc = "surface"

        social.arc_stage = min(
            10,
            int(
                social.conversation_depth * 0.35 +
                social.trust_level * 0.20 +
                social.reflection_depth * 0.20 +
                social.presence_momentum * 0.15 +
                social.unresolved_loops * 0.10
            )
        )

        active_topics = [v for v in self.recent_topic_windows.values() if v > 0]
        social.continuity_score = min(10, len(active_topics))

        self.infer_psychological_signature()


    def _semantic_topic_scores(self, lowered: str) -> dict[str, float]:
        normalized = lowered.lower().strip()

        weighted_roots = {
            "disconnection": {
                "tem algo desconectado": 4, "desconect": 3, "fora do lugar": 4, "fora do eixo": 4,
                "não consigo me achar": 5, "nao consigo me achar": 5, "não consigo me encontrar": 5, "nao consigo me encontrar": 5,
                "sem encaixe": 4, "não caber": 3, "nao caber": 3, "fora do eixo": 4, "desalinhado": 4, "não me localizo": 4, "nao me localizo": 4, "nao caber": 3, "desencontrado": 4, "me prendendo": 3, "não me encontro": 5, "nao me encontro": 5,
            },
            "stagnation": {
                "nada anda": 5, "preso nisso": 5, "travado": 4, "mesmo ponto": 4, "não saio": 3, "nao saio": 3,
                "continua igual": 3, "sem sair disso": 4, "sem deslocamento": 3, "parado": 3, "não anda": 4,
            },
            "clarity_seek": {
                "não consigo entender": 5, "nao consigo entender": 5, "preciso organizar": 4, "linha sobre isso": 4,
                "não faz sentido": 4, "nao faz sentido": 4, "clareza": 3, "estruturar isso": 4, "montar sentido": 3, "organizar minha cabeça": 5, "não monto linha": 5, "nao monto linha": 5, "não consigo organizar": 5, "nao consigo organizar": 5, "tento estruturar": 4,
            },
            "uncertainty": {
                "em aberto": 5, "aberto ainda": 5, "não fecha": 5, "nao fecha": 5, "pendurado em mim": 5,
                "sem conclusão": 5, "inacabado": 4, "continua me rondando": 4, "fechamento": 3, "encerramento": 3,
            },
            "fatigue": {
                "drenado": 5, "sem margem": 4, "desgaste acumulado": 5, "não recomponho": 5, "nao recomponho": 5,
                "sem energia": 4, "exausto": 4, "funcionando sem energia": 5, "sem reposição": 3, "cansado": 3, "não volto": 5, "nao volto": 5, "não recompõe": 5, "nao recompõe": 5, "bateria nunca enche": 5, "vou drenando": 4, "só dreno": 4, "sem força": 4,
            },
            "mental_noise": {
                "ruído": 5, "ruido": 5, "cabeça não aquieta": 5, "cabeca não aquieta": 5, "cabeca nao aquieta": 5,
                "pensamento demais": 5, "penso demais": 5, "barulho demais": 5, "mente acelerada": 5, "mente corre": 5, "não desligo": 4, "nao desligo": 4, "sem foco": 4, "embaralhado": 4, "silêncio mental": 5, "silencio mental": 5,
                "não encontro silêncio": 5, "nao encontro silencio": 5, "mente não para": 4, "mente nao para": 4,
            },
        }

        scores = {}

        for topic, roots in weighted_roots.items():
            topic_score = 0.0

            for root, weight in roots.items():
                if root in normalized:
                    topic_score += weight

            if self._matches_learned_topic(normalized, topic):
                topic_score += 2.0

            topic_score += min(0.35, self.recent_topic_windows.get(topic, 0) * 0.05)

            if self.social_state.current_topic == topic and self._is_contextual_continuation(normalized):
                topic_score += 0.18

            if topic_score > 0:
                scores[topic] = topic_score

        return scores

    def _semantic_emotion_topic(self, lowered: str) -> str | None:
        scores = self._semantic_topic_scores(lowered)
        if not scores:
            return None

        priority = {
            "mental_noise": 6,
            "uncertainty": 5,
            "fatigue": 4,
            "clarity_seek": 3,
            "stagnation": 2,
            "disconnection": 1,
        }

        ranked = sorted(scores.items(), key=lambda x: (x[1], priority.get(x[0], 0)), reverse=True)
        return ranked[0][0]

    def govern_semantic_fusion(self, user_text: str, fused: list[str]) -> tuple[str, str | None, str | None]:
        lowered = user_text.lower().strip()

        semantic_topics = {"fatigue", "mental_noise", "disconnection", "stagnation", "clarity_seek", "uncertainty"}

        if self._is_contextual_continuation(lowered):
            current = self.social_state.current_topic
            if current in semantic_topics:
                inherited = [current] + [x for x in fused if x != current]
                fused = inherited[:3]
            elif not fused:
                fused = ["uncertainty", "stagnation"]

        if not fused:
            fused = ["uncertainty"]

        primary = fused[0] if len(fused) >= 1 else None
        secondary = fused[1] if len(fused) >= 2 else None
        latent = fused[2] if len(fused) >= 3 else None

        return primary or "uncertainty", secondary, latent

    def detect_semantic_topic(self, user_text: str) -> str | None:
        fused = self.detect_semantic_topic_fusion(user_text)
        primary, _, _ = self.govern_semantic_fusion(user_text, fused)
        return primary

    def detect_semantic_topic_fusion(self, user_text: str) -> list[str]:
        lowered = user_text.lower().strip()

        contextual = self._contextual_semantic_topic(lowered)
        scores = self._semantic_topic_scores(user_text)

        if contextual:
            scores[contextual] = scores.get(contextual, 0) + 3.5

        if not scores:
            return ["uncertainty"]

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_score = ranked[0][1]

        cluster = [topic for topic, score in ranked if top_score - score <= 4.2][:3]

        if contextual and contextual not in cluster:
            cluster = [contextual] + cluster
            cluster = cluster[:3]

        return cluster

    def _is_contextual_continuation(self, lowered: str) -> bool:
        continuation_markers = (
            "ainda", "continua", "continuo", "continua igual", "no mesmo", "mesma coisa",
            "suspenso", "nao acabou", "não acabou", "isso continua", "isso ainda", "segue isso", "de novo nisso",
        )

        if len(lowered.split()) == 1 and lowered not in {"continua", "de novo"}:
            return False

        return any(marker in lowered for marker in continuation_markers)


    def _contextual_semantic_topic(self, lowered: str) -> str | None:
        lexical = self._semantic_emotion_topic(lowered)
        if lexical:
            return lexical

        if not self._is_contextual_continuation(lowered):
            return None

        social = self.social_state

        if social.unresolved_loops < 3:
            return None

        if social.current_topic in {
            "fatigue",
            "mental_noise",
            "disconnection",
            "stagnation",
            "clarity_seek",
            "uncertainty",
        }:
            return social.current_topic

        return None

    def _matches_learned_topic(self, lowered: str, topic: str) -> bool:
        patterns = self.learned_patterns.get(topic, [])
        return any(p.lower() in lowered for p in patterns)

