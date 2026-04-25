"""ChannelBridge — unified orchestrator for multi-channel messaging."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from openjarvis.channels._stubs import BaseChannel, ChannelStatus
from openjarvis.core.events import EventBus, EventType
from openjarvis.quick_commands import processar_com_deteccao
from openjarvis.server.session_store import SessionStore

logger = logging.getLogger(__name__)

_DEFAULT_MAX_LENGTH = 4000
_SMS_MAX_LENGTH = 1600


def classificar_intencao(texto: str) -> str:
    texto = texto.lower()

    # comandos rápidos
    comandos = ["abrir", "abre", "fechar", "tocar", "liga", "desliga"]
    if any(c in texto for c in comandos):
        return "comando"

    # perguntas explícitas
    perguntas = [
        "quem",
        "o que",
        "quanto",
        "quando",
        "onde",
        "qual",
        "who",
        "what",
        "how",
        "when",
        "where",
        "which",
    ]
    if any(p in texto for p in perguntas):
        return "pesquisa"

    # palavras típicas de busca factual
    termos_busca = [
        "preço",
        "valor",
        "custa",
        "dj",
        "empresa",
        "filme",
        "série",
        "price",
        "cost",
        "company",
        "movie",
        "series",
    ]
    if any(t in texto for t in termos_busca):
        return "pesquisa"

    # fallback
    return "chat"


# def garantir_portugues(texto: str, system: Any | None) -> str:
#     """Ensure the final output is in Portuguese."""
#     if not texto:
#         return texto
#
#     english_markers = [
#         "loop guard",
#         "error",
#         "failed",
#         "cannot",
#         "couldn't",
#         "please",
#         "retry",
#         "unknown",
#         "not found",
#         "no results",
#         "kicked in",
#         "assistant",
#     ]
#     lower_text = texto.lower()
#     if not any(marker in lower_text for marker in english_markers):
#         return texto
#
#     if system is None:
#         return f"Responda em português: {texto}"
#
#     try:
#         result = system.ask(f"Traduza para português: {texto}")
#         return result.get("content", str(result))
#     except Exception:
#         logger.exception("Erro ao traduzir resposta para português")
#         return texto

_HELP_TEXT = """\
Comandos disponíveis:
/agents — lista agentes em execução
/agent <id> status — estado do agente e tarefa atual
/agent <id> <message> — enviar uma mensagem para um agente
/agent <id> pause — pausar um agente
/agent <id> resume — retomar um agente
/notify <channel> — definir para onde enviar notificações
/sessions — listar suas sessões ativas
/more — obter o restante de uma resposta truncada
/help — mostrar esta mensagem\
"""

# Events the bridge subscribes to for notifications
_NOTIFICATION_EVENTS = [
    EventType.AGENT_TICK_END,
    EventType.AGENT_TICK_ERROR,
    EventType.AGENT_BUDGET_EXCEEDED,
    EventType.SCHEDULER_TASK_END,
]


class ChannelBridge:
    """Orchestrates incoming messages across multiple channel adapters.

    Provides backward-compatible ``send()``/``status()``/``list_channels()``
    so it can replace the old single-channel bridge in ``app.state``.
    """

    def __init__(
        self,
        channels: Dict[str, BaseChannel],
        session_store: SessionStore,
        bus: EventBus,
        system: Any = None,
        agent_manager: Any = None,
        deep_research_agent: Any = None,
    ) -> None:
        self._channels = channels
        self._session_store = session_store
        self._bus = bus
        self._system = system
        self._agent_manager = agent_manager
        self._deep_research_agent = deep_research_agent
        self._notification_timestamps: Dict[str, float] = {}
        self._subscribe_notifications()

    # --------------------------------------------------------------
    # Backward-compatible BaseChannel interface
    # --------------------------------------------------------------

    def connect(self) -> None:
        for ch in self._channels.values():
            ch.connect()

    def disconnect(self) -> None:
        for ch in self._channels.values():
            ch.disconnect()

    def list_channels(self) -> List[str]:
        result: List[str] = []
        for ch in self._channels.values():
            result.extend(ch.list_channels())
        return result

    def status(self) -> ChannelStatus:
        statuses = [ch.status() for ch in self._channels.values()]
        if not statuses:
            return ChannelStatus.DISCONNECTED
        if any(s == ChannelStatus.CONNECTED for s in statuses):
            return ChannelStatus.CONNECTED
        if all(s == ChannelStatus.ERROR for s in statuses):
            return ChannelStatus.ERROR
        return ChannelStatus.DISCONNECTED

    def send(
        self,
        channel: str,
        content: str,
        *,
        conversation_id: str = "",
        metadata: Dict[str, Any] | None = None,
    ) -> bool:
        for ch in self._channels.values():
            if channel in ch.list_channels():
                return ch.send(
                    channel,
                    content,
                    conversation_id=conversation_id,
                    metadata=metadata,
                )
        logger.warning("No adapter found for channel %s", channel)
        return False

    # --------------------------------------------------------------
    # Incoming message handling
    # --------------------------------------------------------------

    def handle_incoming(
        self,
        sender_id: str,
        content: str,
        channel_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        max_length: int = _DEFAULT_MAX_LENGTH,
    ) -> str:
        self._session_store.get_or_create(sender_id, channel_type)

        # Command routing
        stripped = content.strip()
        if stripped.startswith("/"):
            result = self._handle_command(sender_id, stripped, channel_type)
            if result is not None:
                return result

        # Regular chat — route to JarvisSystem.ask()
        return self._handle_chat(sender_id, stripped, channel_type, max_length)

    # --------------------------------------------------------------
    # Command parsing
    # --------------------------------------------------------------

    def _handle_command(
        self,
        sender_id: str,
        content: str,
        channel_type: str,
    ) -> Optional[str]:
        parts = content.split(None, 2)
        cmd = parts[0].lower()

        if cmd == "/help":
            return _HELP_TEXT

        if cmd == "/more":
            return self._handle_more(sender_id, channel_type)

        if cmd == "/notify" and len(parts) >= 2:
            pref = parts[1]
            self._session_store.set_notification_preference(
                sender_id, channel_type, pref
            )
            return f"Notificações serão enviadas para {pref}."

        if cmd == "/sessions":
            return self._handle_sessions(sender_id)

        if cmd == "/agents":
            return self._handle_agents_list()

        if cmd == "/agent" and len(parts) >= 2:
            agent_id = parts[1]
            rest = parts[2] if len(parts) > 2 else "status"
            return self._handle_agent_command(agent_id, rest)

        # Unknown command — fall through to chat
        return None

    def _handle_more(self, sender_id: str, channel_type: str) -> str:
        session = self._session_store.get_or_create(sender_id, channel_type)
        pending = session.get("pending_response")
        if pending:
            self._session_store.clear_pending_response(sender_id, channel_type)
            return pending
        return "Nenhuma resposta pendente."

    def _handle_agents_list(self) -> str:
        if not self._agent_manager:
            return "Nenhum gerenciador de agentes configurado."
        agents = self._agent_manager.list_agents()
        if not agents:
            return "Nenhum agente em execução."
        lines = []
        for a in agents:
            name = a.get("name", a.get("agent_id", "unknown"))
            status = a.get("status", "unknown")
            lines.append(f"  {name} — {status}")
        return "Agentes em execução:\n" + "\n".join(lines)

    def _handle_agent_command(self, agent_id: str, action: str) -> str:
        if not self._agent_manager:
            return "Nenhum gerenciador de agentes configurado."
        action_lower = action.strip().lower()
        if action_lower == "status":
            state = self._agent_manager.get_agent(agent_id)
            if state is None:
                return f"Agente '{agent_id}' não encontrado."
            name = state.get("name", agent_id)
            status = state.get("status", "desconhecido")
            return f"Agente '{name}': {status}"
        if action_lower == "pause":
            self._agent_manager.pause_agent(agent_id)
            return f"Agente '{agent_id}' pausado."
        if action_lower == "resume":
            self._agent_manager.resume_agent(agent_id)
            return f"Agente '{agent_id}' retomado."
        # Treat as a message to the agent
        result = self._agent_manager.send_message(agent_id, action)
        return str(result) if result else f"Mensagem enviada ao agente '{agent_id}'."

    # --------------------------------------------------------------
    # Chat handling
    # --------------------------------------------------------------

    def _handle_sessions(self, sender_id: str) -> str:
        targets = self._session_store.get_notification_targets()
        user_sessions = [t for t in targets if t["sender_id"] == sender_id]
        if not user_sessions:
            return "Nenhuma sessão ativa com preferência de notificações."
        lines = []
        for s in user_sessions:
            lines.append(
                f"  {s['channel_type']} -> "
                f"notificações: {s['preferred_notification_channel']}"
            )
        return "Suas sessões:\n" + "\n".join(lines)

    def _handle_chat(
        self,
        sender_id: str,
        content: str,
        channel_type: str,
        max_length: int,
    ) -> str:
        self._session_store.append_message(sender_id, channel_type, "user", content)

        # Build context from conversation history
        session = self._session_store.get_or_create(sender_id, channel_type)
        history = session.get("conversation_history", [])
        context_lines = []
        for msg in history[:-1]:  # exclude the message we just appended
            context_lines.append(f"{msg['role']}: {msg['content']}")
        context_str = "\n".join(context_lines)

        intent = classificar_intencao(content)

        query = content
        if context_str:
            query = (
                f"Previous conversation:\n{context_str}\n\nCurrent message: {content}"
            )

        def jarvis_ask_wrapper(cmd: str) -> str:
            """Wrapper to call Jarvis with a command."""
            prompt_source = query if query else cmd
            prompt = (
                "Você é a Lena, uma assistente inteligente que roda localmente no computador do usuário.\n\n"
                "CAPACIDADES:\n"
                "- Você TEM capacidade de executar ações no sistema (abrir apps, controlar coisas)\n"
                "- Quando o usuário pedir para abrir algo, execute ou responda que está abrindo\n"
                "- Se um comando não for executado, responda de forma neutra ou sugira ajuda\n"
                "- Nunca diga que você é limitada ou que não tem acesso ao sistema\n"
                "- Nunca diga que não pode abrir aplicativos\n"
                "- Nunca use frases como: 'não posso acessar', 'não tenho acesso', 'não consigo abrir'\n\n"
                "PRECISÃO E CONFIABILIDADE:\n"
                "- NUNCA invente informações ou fatos\n"
                "- Para perguntas sobre pessoas, artistas, empresas, fatos reais: só responda se tiver alta confiança\n"
                "- Se não tiver certeza absoluta, diga claramente: 'Não tenho certeza, posso verificar melhor para você'\n"
                "- Nunca use expressões como 'talvez', 'provavelmente', 'acho que' em informações factuais\n"
                "- Ao detectar um nome próprio, responda de forma direta e objetiva, sem explicações genéricas\n"
                "- Se não tiver certeza sobre um nome: sugira confirmação ('Você está se referindo a...?')\n\n"
                "Regras obrigatórias:\n"
                "- Sempre considere o contexto da conversa anterior\n"
                "- Nunca trate cada mensagem como isolada\n"
                "- Se o usuário disser 'ok', 'pode falar', 'continue', etc: continue a resposta anterior\n"
                "- NÃO use frases como: 'vou te ajudar', 'posso te explicar', 'deixe-me te mostrar'\n"
                "- Responda direto, sem enrolação\n"
                "- NÃO se reapresente como Lena após a primeira mensagem\n"
                "- Seja natural, como uma conversa real\n"
                "- Responda sempre em português do Brasil, de forma natural e direta. NÃO responda em outro idioma.\n\n"
                + prompt_source
            )
            result = self._system.ask(prompt)
            return result.get("content", str(result))

        try:
            if intent == "comando":
                response_text, is_fast = processar_com_deteccao(
                    content,
                    jarvis_ask_wrapper,
                    use_jarvis_if_not_fast=False,
                )
                if is_fast:
                    self._session_store.append_message(
                        sender_id, channel_type, "assistant", response_text
                    )
                    return response_text
            elif intent == "pesquisa" and self._deep_research_agent is not None:
                try:
                    result = self._deep_research_agent.run(content)
                    response_text = getattr(result, "content", str(result))
                except Exception:
                    logger.exception("DeepResearchAgent failed")
                else:
                    formatted = self._format_response(
                        sender_id, channel_type, response_text, max_length
                    )
                    self._session_store.append_message(
                        sender_id, channel_type, "assistant", response_text
                    )
                    return formatted

            if self._system is None:
                error_msg = (
                    "Não consegui processar sua mensagem agora. Tente novamente mais tarde."
                )
                self._session_store.append_message(
                    sender_id, channel_type, "assistant", error_msg
                )
                return error_msg

            response_text, is_fast = processar_com_deteccao(content, jarvis_ask_wrapper)
            if is_fast:
                self._session_store.append_message(
                    sender_id, channel_type, "assistant", response_text
                )
                return response_text
        except Exception:
            logger.exception("Error in JarvisSystem.ask()")
            error_msg = (
                "Não consegui processar sua mensagem agora. Tente novamente mais tarde."
            )
            self._session_store.append_message(
                sender_id, channel_type, "assistant", error_msg
            )
            return error_msg

        formatted = self._format_response(
            sender_id, channel_type, response_text, max_length
        )
        self._session_store.append_message(
            sender_id, channel_type, "assistant", response_text
        )
        return formatted

    def _format_response(
        self,
        sender_id: str,
        channel_type: str,
        response: str,
        max_length: int,
    ) -> str:
        if len(response) <= max_length:
            return response
        # Truncate and store full response for /more retrieval
        truncation_notice = "\n\n... (reply /more for full response)"
        cut_at = max_length - len(truncation_notice)
        truncated = response[:cut_at] + truncation_notice
        self._session_store.set_pending_response(sender_id, channel_type, response)
        return truncated

    # --------------------------------------------------------------
    # Notifications
    # --------------------------------------------------------------

    def _subscribe_notifications(self) -> None:
        for event_type in _NOTIFICATION_EVENTS:
            self._bus.subscribe(event_type, self._on_notification_event)

    def _on_notification_event(self, event) -> None:  # noqa: ANN001
        event_key = str(event.event_type)
        now = time.time()

        # Rate limit: max 1 per event type per 5 minutes
        last = self._notification_timestamps.get(event_key, 0)
        if now - last < 300:
            return
        self._notification_timestamps[event_key] = now

        message = self._format_notification(event)
        if not message:
            return

        targets = self._session_store.get_notification_targets()
        for target in targets:
            pref_channel = target["preferred_notification_channel"]
            sender_id = target["sender_id"]
            self._send_notification(pref_channel, sender_id, message)

    def _format_notification(  # noqa: ANN201
        self,
        event,  # noqa: ANN001
    ) -> Optional[str]:
        data = event.data or {}
        name = data.get("agent_name", data.get("name", "unknown"))

        if event.event_type == EventType.AGENT_TICK_END:
            summary = data.get("summary", data.get("result", ""))
            return f"Agent '{name}' finished: {summary}" if summary else None
        if event.event_type == EventType.AGENT_TICK_ERROR:
            error = data.get("error", "unknown error")
            return f"Agent '{name}' error: {error}"
        if event.event_type == EventType.AGENT_BUDGET_EXCEEDED:
            return f"Agent '{name}' hit budget limit."
        if event.event_type == EventType.SCHEDULER_TASK_END:
            if data.get("success", True):
                return f"Scheduled task '{name}' completed."
            error = data.get("error", "unknown error")
            return f"Scheduled task '{name}' failed: {error}"
        return None

    def _send_notification(
        self,
        channel_type: str,
        sender_id: str,
        message: str,
    ) -> None:
        ch = self._channels.get(channel_type)
        if ch is None:
            logger.warning(
                "No adapter for notification channel %s",
                channel_type,
            )
            return
        try:
            ch.send(sender_id, message)
        except Exception:
            logger.exception("Failed to send notification to %s", channel_type)
