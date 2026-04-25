from __future__ import annotations
import asyncio
import logging
import socket
import sys
import time
import uuid
import json
from typing import Optional, Any, Dict, List, Callable
from pathlib import Path

import click
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

from openjarvis.core.config import load_config
from openjarvis.core.events import EventBus
from openjarvis.engine import discover_engines, discover_models, get_engine
from openjarvis.intelligence import (
    merge_discovered_models,
    register_builtin_models,

)
from openjarvis.core.types import Message, Role

from openjarvis.agent.lena_agent import LenaAgent

logger = logging.getLogger(__name__)

# ==========================================
# 🔥 MELHORIA #6: Memory file correto
# ==========================================
BASE_DIR = Path(__file__).parent
MEMORY_PATH = BASE_DIR / "memory.json"


def estimate_prompt_tokens(messages: List[Message]) -> int:
    """Estimate token count for messages (simple approximation)."""
    total_chars = sum(len(m.content) for m in messages)
    # Rough estimate: ~4 characters per token
    return max(1, total_chars // 4)


def _to_role(role_str: str) -> Role:
    """Convert string role to Role enum."""
    role_map = {'user': Role.USER, 'assistant': Role.ASSISTANT, 'system': Role.SYSTEM}
    return role_map.get(role_str.lower(), Role.USER)


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex((host, port)) == 0


# ==========================================
# 🔥 MELHORIA #1: Função para RAG simples
# ==========================================
def _calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple word-overlap similarity score (Jaccard similarity).
    Used for intelligent memory retrieval.
    """
    if not text1 or not text2:
        return 0.0
    
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union) if union else 0.0

# =========================
# SERVER
# =========================
@click.command()
@click.option("--host", default=None)
@click.option("--port", default=None, type=int)
@click.option("-e", "--engine", "engine_key", default=None)
@click.option("-m", "--model", "model_name", default=None)
@click.option("-a", "--agent", "agent_name", default=None)
def serve(
    host: Optional[str],
    port: Optional[int],
    engine_key: Optional[str],
    model_name: Optional[str],
    agent_name: Optional[str],
) -> None:

    try:
        import uvicorn
    except ImportError:
        print("Install: uv sync --extra server")
        sys.exit(1)

    config = load_config()

    bind_host = host or config.server.host
    bind_port = port or config.server.port

    if _port_in_use(bind_host, bind_port):
        bind_port += 1

    register_builtin_models()

    bus: EventBus = EventBus(record_history=False)

    resolved = get_engine(config, engine_key)
    if resolved is None:
        print("No inference engine available")
        sys.exit(1)

    engine_name, engine = resolved

    all_engines = discover_engines(config)
    all_models = discover_models(all_engines)

    for ek, model_ids in all_models.items():
        merge_discovered_models(ek, model_ids)

    if model_name is None:
        model_name = "phi3"

    if not model_name:
        engine_models = all_models.get(engine_name, [])
        if not engine_models:
            print("No models available")
            sys.exit(1)
        model_name = engine_models[0]

    agent = LenaAgent(engine=engine, model=model_name)

    # =========================
    # 🔥 APP PRINCIPAL (GATEWAY)
    # =========================
    app = FastAPI(
        title="OpenJarvis API with Lena",
        description="OpenAI-compatible API server with Lena agent integration",
        version="0.1.0",
    )

    from fastapi.middleware.cors import CORSMiddleware

    _origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # =========================
    # 🔥 ENDPOINT #1: Chat (Compatível com OpenAI)
    # =========================
    @app.post("/v1/chat/completions")
    async def lena_chat(request: Request):
        logger.info(f"[LENA] intercepted {request.url.path}")

        data = await request.json()
        messages = data.get("messages", [])

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, agent.run, messages)

        return JSONResponse(content=result)

    # =========================
    # 🔥 ENDPOINT #2: Chat com Stream
    # =========================
    @app.post("/v1/chat/stream")
    async def lena_chat_stream(request: Request):
        logger.info(f"[LENA] intercepted stream {request.url.path}")

        data = await request.json()
        messages = data.get("messages", [])

        def generate():
            for chunk in agent.run_stream(messages):
                yield chunk

        return StreamingResponse(generate(), media_type="text/event-stream")

    # =========================
    # 🔥 ENDPOINT #3: Memória
    # =========================
    @app.get("/v1/memory")
    async def get_memory():
        logger.info(f"[LENA] accessed memory endpoint")
        
        memory_snapshot = {
            "short_term": list(agent.memory["short_term"]),
            "long_term": agent.memory["long_term"],
            "short_term_count": len(agent.memory["short_term"]),
            "long_term_count": len(agent.memory["long_term"]),
            "timestamp": int(time.time())
        }
        
        return JSONResponse(content=memory_snapshot)

    # =========================
    # 🔥 CONFIGURAÇÃO DO OPENJARVIS (SEM ROTA CONFLITANTE)
    # =========================
    # Store dependencies in app state (copiado do create_app)
    app.state.engine = engine
    app.state.model = model_name
    app.state.agent = agent
    app.state.bus = bus
    app.state.engine_name = engine_name
    app.state.agent_name = "lena"
    channel_bridge = None  # Definir channel_bridge
    app.state.channel_bridge = channel_bridge
    app.state.config = config
    app.state.memory_backend = None
    app.state.speech_backend = None
    app.state.agent_manager = None
    app.state.agent_scheduler = None
    app.state.session_start = time.time()

    # Wire up trace store if traces are enabled
    app.state.trace_store = None
    try:
        from openjarvis.traces.store import TraceStore

        cfg = config
        if cfg.traces.enabled:
            _trace_store = TraceStore(db_path=cfg.traces.db_path)
            app.state.trace_store = _trace_store
            _bus = getattr(app.state, "bus", None)
            if _bus is not None:
                _trace_store.subscribe_to_bus(_bus)
    except Exception:
        pass  # traces are optional

    # Include routers (EXCETO o router principal que tem /v1/chat/completions)
    from openjarvis.server.comparison import comparison_router
    from openjarvis.server.connectors_router import create_connectors_router
    from openjarvis.server.dashboard import dashboard_router
    from openjarvis.server.digest_routes import create_digest_router
    from openjarvis.server.upload_router import router as upload_router
    from openjarvis.server.api_routes import include_all_routes

    app.include_router(dashboard_router)
    app.include_router(comparison_router)
    app.include_router(create_connectors_router())
    app.include_router(create_digest_router())
    app.include_router(upload_router)
    include_all_routes(app)

    # Restore SendBlue channel bindings
    try:
        mgr = getattr(app.state, "agent_manager", None)
        if mgr is not None:
            for agent_info in mgr.list_agents():
                agent_id = agent_info.get("id", agent_info.get("agent_id", ""))
                bindings = mgr.list_channel_bindings(agent_id)
                for b in bindings:
                    if b.get("channel_type") != "sendblue":
                        continue
                    config_bind = b.get("config", {})
                    api_key_id = config_bind.get("api_key_id", "")
                    api_secret_key = config_bind.get("api_secret_key", "")
                    from_number = config_bind.get("from_number", "")
                    if not api_key_id or not api_secret_key:
                        continue

                    from openjarvis.channels.sendblue import SendBlueChannel

                    channel = SendBlueChannel(
                        api_key_id=api_key_id,
                        api_secret_key=api_secret_key,
                        from_number=from_number,
                    )
                    if channel_bridge is not None:
                        channel_bridge.add_channel(channel)
                    logger.info("Restored SendBlue binding for agent %s", agent_id)
    except Exception as exc:
        logger.debug("SendBlue binding restore skipped: %s", exc)

    # Add security headers middleware
    try:
        from openjarvis.server.middleware import create_security_middleware

        middleware_cls = create_security_middleware()
        if middleware_cls is not None:
            app.add_middleware(middleware_cls)
    except Exception:
        pass

    # API key authentication middleware
    api_key = getattr(config, 'api_key', None) or ""
    if api_key:
        try:
            from openjarvis.server.auth_middleware import AuthMiddleware

            app.add_middleware(AuthMiddleware, api_key=api_key)
        except Exception:
            pass

    # Mount webhook routes
    webhook_config = getattr(config, 'webhook', None)
    if webhook_config:
        try:
            from openjarvis.server.webhook_routes import create_webhook_router

            webhook_router = create_webhook_router(
                bridge=channel_bridge,
                twilio_auth_token=webhook_config.get("twilio_auth_token", ""),
                bluebubbles_password=webhook_config.get("bluebubbles_password", ""),
                whatsapp_verify_token=webhook_config.get("whatsapp_verify_token", ""),
                whatsapp_app_secret=webhook_config.get("whatsapp_app_secret", ""),
            )
            app.include_router(webhook_router)
        except Exception:
            pass

    # Serve static frontend assets
    import pathlib
    static_dir = pathlib.Path(__file__).parent.parent / "server" / "static"
    if static_dir.is_dir():
        from fastapi.staticfiles import StaticFiles
        from fastapi.responses import FileResponse

        assets_dir = static_dir / "assets"
        if assets_dir.is_dir():
            class _NoCacheStaticFiles(StaticFiles):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)

            _NO_CACHE_HEADERS = {
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            }

            app.mount(
                "/assets",
                _NoCacheStaticFiles(directory=assets_dir),
                name="static-assets",
            )

        @app.get("/{full_path:path}")
        async def spa_catch_all(full_path: str):
            """Serve static files directly, fall back to index.html for SPA routes."""
            if full_path:
                candidate = (static_dir / full_path).resolve()
                resolved_root = static_dir.resolve()
                if candidate.is_relative_to(resolved_root) and candidate.is_file():
                    return FileResponse(candidate, headers=_NO_CACHE_HEADERS)
            return FileResponse(
                static_dir / "index.html",
                headers=_NO_CACHE_HEADERS,
            )

    print(
        f"\nOpenJarvis running\n"
        f"Engine: {engine_name}\n"
        f"Model: {model_name}\n"
        f"URL: http://{bind_host}:{bind_port}\n"
    )

    uvicorn.run(app, host=bind_host, port=bind_port, log_level="info")

if __name__ == "__main__":
    serve()

# if __name__ == "__main__":
#     import uvicorn

#     serve(
#         host="127.0.0.1",
#         port=8001,
#         engine_key=None,
#         model_name=None,
#         agent_name=None
#     )