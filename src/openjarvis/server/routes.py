# path: openjarvis/server/routes.py

from __future__ import annotations

import logging
import uuid
from typing import List

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from openjarvis.core.types import Message, Role
from openjarvis.quick_commands import processar_com_deteccao
from openjarvis.server.models import (
    ChatCompletionChunk,
    ChatCompletionRequest,
    ChatCompletionResponse,
    Choice,
    ChoiceMessage,
    DeltaMessage,
    StreamChoice,
    UsageInfo,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# -------------------------------
# UTIL
# -------------------------------
def _to_messages(chat_messages) -> List[Message]:
    messages: List[Message] = []

    for m in chat_messages:
        role = Role(m.role) if m.role in {r.value for r in Role} else Role.USER
        messages.append(Message(role=role, content=m.content or ""))

    return messages


# -------------------------------
# NON-STREAM
# -------------------------------
def _handle_direct(engine, model: str, req: ChatCompletionRequest) -> ChatCompletionResponse:
    # 🔥 lazy import (corrige erro linha 12)
    from openjarvis.azure_integration import route_message

    messages = _to_messages(req.messages)

    messages_dict = [
        {"role": m.role.value, "content": m.content}
        for m in messages
    ]

    def usar_fluxo_local(msgs_dict):
        local_messages = _to_messages(msgs_dict)

        result = engine.generate(
            local_messages,
            model=model,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        )

        return result.get("content", "")

    content = "".join(route_message(messages_dict, usar_fluxo_local))

    return ChatCompletionResponse(
        model=model,
        choices=[
            Choice(
                message=ChoiceMessage(role="assistant", content=content),
                finish_reason="stop",
            )
        ],
        usage=UsageInfo(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
        ),
    )


# -------------------------------
# STREAM
# -------------------------------
async def _handle_stream(engine, model: str, req: ChatCompletionRequest):
    # 🔥 lazy import (corrige erro linha 12)
    from openjarvis.azure_integration import route_message

    messages = _to_messages(req.messages)

    messages_dict = [
        {"role": m.role.value, "content": m.content}
        for m in messages
    ]

    chunk_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"

    def usar_fluxo_local(msgs_dict):
        local_messages = _to_messages(msgs_dict)

        result = engine.generate(
            local_messages,
            model=model,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        )

        return result.get("content", "")

    async def generate():
        # início
        yield f"data: {ChatCompletionChunk(id=chunk_id, model=model, choices=[StreamChoice(delta=DeltaMessage(role='assistant'))]).model_dump_json()}\n\n"

        try:
            # 🔥 pipeline único
            for chunk_text in route_message(messages_dict, usar_fluxo_local):
                chunk = ChatCompletionChunk(
                    id=chunk_id,
                    model=model,
                    choices=[
                        StreamChoice(
                            delta=DeltaMessage(content=chunk_text),
                        )
                    ],
                )

                yield f"data: {chunk.model_dump_json()}\n\n"

        except Exception as exc:
            logger.error("Stream error: %s", exc)

        # fim
        yield f"data: {ChatCompletionChunk(id=chunk_id, model=model, choices=[StreamChoice(delta=DeltaMessage(), finish_reason='stop')]).model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# -------------------------------
# ROUTE PRINCIPAL
# -------------------------------
@router.post("/v1/chat/completions")
async def chat_completions(request_body: ChatCompletionRequest, request: Request):
    engine = request.app.state.engine
    model = request_body.model
    
    # ✅ AGENT OVERRIDE (se existir)
    agent = getattr(request.app.state, "agent", None)
    if agent is not None and hasattr(agent, "run"):
        try:
            content = agent.run(request_body.messages)
            return ChatCompletionResponse(
                model=model,
                choices=[
                    Choice(
                        message=ChoiceMessage(role="assistant", content=content),
                        finish_reason="stop",
                    )
                ],
            )
        except Exception as exc:
            logger.error("Agent error: %s", exc)
            # Fallback para fluxo normal
            pass
    
    # ⚡ FAST PATH
    query_text = ""
    for m in reversed(request_body.messages):
        if m.role == "user" and m.content:
            query_text = m.content
            break
    if query_text:
        response_text, is_fast = processar_com_deteccao(
            query_text,
            lambda _: "",
            use_jarvis_if_not_fast=False,
        )
        if is_fast:
            return ChatCompletionResponse(
                model=model,
                choices=[
                    Choice(
                        message=ChoiceMessage(role="assistant", content=response_text),
                        finish_reason="stop",
                    )
                ],
            )
    if request_body.stream:
        return await _handle_stream(engine, model, request_body)
    return _handle_direct(engine, model, request_body)
