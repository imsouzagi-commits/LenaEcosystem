# path: src/openjarvis/server/routes.py

from __future__ import annotations

import logging
import uuid
from typing import List

from fastapi import APIRouter
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


def _to_messages(chat_messages) -> List[Message]:
    messages: List[Message] = []
    valid_roles = {r.value for r in Role}

    for m in chat_messages:
        role = Role(m.role) if m.role in valid_roles else Role.USER
        messages.append(Message(role=role, content=m.content or ""))

    return messages


def _to_dict_messages(chat_messages) -> List[dict]:
    return [
        {
            "role": m.role,
            "content": m.content or "",
        }
        for m in chat_messages
    ]


def _handle_direct(agent, model: str, req: ChatCompletionRequest) -> ChatCompletionResponse:
    response = agent.run(_to_dict_messages(req.messages))
    content = response["choices"][0]["message"]["content"]

    return ChatCompletionResponse(
        model=model,
        choices=[
            Choice(
                message=ChoiceMessage(
                    role="assistant",
                    content=content,
                ),
                finish_reason="stop",
            )
        ],
        usage=UsageInfo(
            prompt_tokens=response.get("usage", {}).get("prompt_tokens", 0),
            completion_tokens=response.get("usage", {}).get("completion_tokens", 0),
            total_tokens=response.get("usage", {}).get("total_tokens", 0),
        ),
    )


async def _handle_stream(agent, model: str, req: ChatCompletionRequest):
    from openjarvis.azure_integration import route_message

    messages_dict = _to_dict_messages(req.messages)
    chunk_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"

    def usar_fluxo_local(msgs_dict):
        result = agent.run(msgs_dict)
        return result["choices"][0]["message"]["content"]

    async def generate():
        yield f"data: {ChatCompletionChunk(id=chunk_id, model=model, choices=[StreamChoice(delta=DeltaMessage(role='assistant'))]).model_dump_json()}\n\n"

        try:
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

        yield f"data: {ChatCompletionChunk(id=chunk_id, model=model, choices=[StreamChoice(delta=DeltaMessage(), finish_reason='stop')]).model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/v1/chat/completions/fallback")
async def chat_completions(request_body: ChatCompletionRequest):
    from openjarvis.cli.serve import app

    agent = app.state.agent
    model = request_body.model

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
                        message=ChoiceMessage(
                            role="assistant",
                            content=response_text,
                        ),
                        finish_reason="stop",
                    )
                ],
                usage=UsageInfo(
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                ),
            )

    if request_body.stream:
        return await _handle_stream(agent, model, request_body)

    return _handle_direct(agent, model, request_body)