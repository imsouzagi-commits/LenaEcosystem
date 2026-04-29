from __future__ import annotations

import logging
from typing import Any, AsyncGenerator, Dict, List

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

from openjarvis.agent.lena_agent import LenaAgent
from openjarvis.server.routes import router

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_app() -> FastAPI:
    app = FastAPI(title="OpenJarvis + Lena")

    lena = LenaAgent()

    app.state.agent = lena

    @app.post("/v1/chat/completions")
    async def lena_chat(request: Request):
        logger.info("[LENA] intercepted /v1/chat/completions")

        try:
            data: Dict[str, Any] = await request.json()
            messages: List[Dict[str, Any]] = data.get("messages", [])
            stream = bool(data.get("stream", False))

            if stream:

                async def event_stream() -> AsyncGenerator[str, None]:
                    async for chunk in lena.run_stream_async(messages):
                        yield chunk
                    yield "data: [DONE]\n\n"

                return StreamingResponse(
                    event_stream(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                    },
                )

            result = lena.run(messages)
            return JSONResponse(content=result)

        except Exception as exc:
            logger.error("[LENA] route error: %s", exc)
            return JSONResponse(
                status_code=500,
                content={
                    "error": str(exc),
                    "object": "error",
                },
            )

    app.include_router(router)

    @app.get("/health")
    async def health():
        return {"status": "ok", "agent": "lena"}

    return app


app = create_app()


def serve() -> None:
    uvicorn.run(
        "openjarvis.cli.serve:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    serve()