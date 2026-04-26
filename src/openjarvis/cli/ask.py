"""``jarvis ask`` — send a query to the assistant."""

from __future__ import annotations

import json as json_mod
import logging
import sys
import time

import click
from rich.console import Console
from rich.table import Table

from openjarvis.cli._tool_names import resolve_tool_names
from openjarvis.cli.hints import hint_no_engine
from openjarvis.core.config import load_config
from openjarvis.core.events import EventBus, EventType
from openjarvis.core.types import Message, Role
from openjarvis.engine import (
    EngineConnectionError,
    discover_engines,
    discover_models,
    get_engine,
)
from openjarvis.intelligence import merge_discovered_models, register_builtin_models
from openjarvis.lena.kernel import LenaKernel
from openjarvis.quick_commands import (
    eh_comando_simples,
    executar_comando_simples,
    processar_comando,
)
from openjarvis.telemetry.instrumented_engine import InstrumentedEngine
from openjarvis.telemetry.store import TelemetryStore

logger = logging.getLogger(__name__)

_LENA_SINGLETON: LenaKernel | None = None


def _get_lena_kernel(engine, model_name: str) -> LenaKernel:
    global _LENA_SINGLETON

    if _LENA_SINGLETON is None:
        _LENA_SINGLETON = LenaKernel(engine=engine, model=model_name)
    else:
        _LENA_SINGLETON.engine = engine
        _LENA_SINGLETON.default_model = model_name

    return _LENA_SINGLETON


def _get_memory_backend(config):
    try:
        import openjarvis.tools.storage  # noqa: F401
        from openjarvis.core.registry import MemoryRegistry

        key = config.memory.default_backend
        if not MemoryRegistry.contains(key):
            return None

        backend = (
            MemoryRegistry.create(key, db_path=config.memory.db_path)
            if key == "sqlite"
            else MemoryRegistry.create(key)
        )

        if hasattr(backend, "count") and backend.count() == 0:
            if hasattr(backend, "close"):
                backend.close()
            return None

        return backend

    except Exception as exc:
        logger.debug("Memory backend unavailable: %s", exc)
        return None


def _build_tools(tool_names: list[str], config, engine, model_name: str):
    from openjarvis.core.registry import ToolRegistry

    tools = []

    for name in tool_names:
        name = name.strip()
        if not name or not ToolRegistry.contains(name):
            continue

        tool_cls = ToolRegistry.get(name)

        if name == "retrieval":
            backend = _get_memory_backend(config)
            tools.append(tool_cls(backend=backend))
        elif name == "llm":
            tools.append(tool_cls(engine=engine, model=model_name))
        else:
            tools.append(tool_cls())

    return tools


def _run_agent(
    agent_name: str,
    query_text: str,
    engine,
    model_name: str,
    tool_names: list[str],
    config,
    bus: EventBus,
    temperature: float,
    max_tokens: int,
    capability_policy=None,
):
    import openjarvis.agents  # noqa
    from openjarvis.agents._stubs import AgentContext
    from openjarvis.core.registry import AgentRegistry

    if not AgentRegistry.contains(agent_name):
        raise click.ClickException(
            f"Unknown agent: {agent_name}. Available: {', '.join(AgentRegistry.keys())}"
        )

    agent_cls = AgentRegistry.get(agent_name)

    tools = []
    if tool_names:
        import openjarvis.tools  # noqa
        tools = _build_tools(tool_names, config, engine, model_name)

    agent_kwargs = {
        "bus": bus,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if getattr(agent_cls, "accepts_tools", False):
        agent_kwargs["tools"] = tools
        agent_kwargs["max_turns"] = config.agent.max_turns
        agent_kwargs["interactive"] = True
        agent_kwargs["confirm_callback"] = lambda prompt: True

    if capability_policy is not None:
        agent_kwargs["capability_policy"] = capability_policy

    agent = agent_cls(engine, model_name, **agent_kwargs)
    ctx = AgentContext()

    return agent.run(query_text, context=ctx)


def _print_profile(
    bus: EventBus,
    wall_seconds: float,
    engine_name: str,
    model_name: str,
    console: Console,
    complexity_result=None,
) -> None:
    inf_events = [e for e in bus.history if e.event_type == EventType.INFERENCE_END]
    if not inf_events:
        return

    total_calls = len(inf_events)
    total_latency = sum(e.data.get("latency", 0.0) for e in inf_events)
    total_tokens = sum(
        e.data.get("usage", {}).get("completion_tokens", 0)
        or e.data.get("completion_tokens", 0)
        for e in inf_events
    )

    table = Table(title=f"Inference Profile ({engine_name} / {model_name})")
    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Calls", str(total_calls))
    table.add_row("Latency", f"{total_latency:.3f}s")
    table.add_row("Tokens", str(total_tokens))
    table.add_row("Wall", f"{wall_seconds:.3f}s")

    console.print(table)


@click.command()
@click.argument("query", nargs=-1, required=True)
@click.option("-m", "--model", "model_name", default=None)
@click.option("-e", "--engine", "engine_key", default=None)
@click.option("-t", "--temperature", default=None, type=float)
@click.option("--max-tokens", default=None, type=int)
@click.option("--json", "output_json", is_flag=True)
@click.option("--no-stream", is_flag=True)
@click.option("--no-context", is_flag=True)
@click.option("-a", "--agent", "agent_name", default=None)
@click.option("--tools", "tool_names", default=None)
@click.option("--profile", "enable_profile", is_flag=True)
def ask(
    query: tuple[str, ...],
    model_name: str | None,
    engine_key: str | None,
    temperature: float | None,
    max_tokens: int | None,
    output_json: bool,
    no_stream: bool,
    no_context: bool,
    agent_name: str | None,
    tool_names: str | None,
    enable_profile: bool,
) -> None:
    console = Console(stderr=True)
    query_text = " ".join(query)
    wall_start = time.monotonic() if enable_profile else 0.0

    config = load_config()
    user_set_max_tokens = max_tokens is not None

    if temperature is None:
        temperature = config.intelligence.temperature
    if max_tokens is None:
        max_tokens = config.intelligence.max_tokens

    from openjarvis.learning.routing.complexity import (
        ComplexityResult,
        adjust_tokens_for_model,
        score_complexity,
    )

    complexity_result: ComplexityResult = score_complexity(query_text)

    bus = EventBus(record_history=True)
    telem_store: TelemetryStore | None = None

    if config.telemetry.enabled:
        try:
            telem_store = TelemetryStore(config.telemetry.db_path)
            telem_store.subscribe_to_bus(bus)
        except Exception as exc:
            logger.debug("Telemetry init failed: %s", exc)

    register_builtin_models()

    effective_engine_key = engine_key or config.intelligence.preferred_engine or None
    resolved = get_engine(config, effective_engine_key)

    if resolved is None:
        console.print("[red bold]No inference engine available.[/red bold]")
        sys.exit(1)

    engine_name, engine = resolved

    from openjarvis.security import setup_security
    sec = setup_security(config, engine, bus)
    engine = sec.engine

    engine = InstrumentedEngine(engine, bus, energy_monitor=None)

    all_engines = discover_engines(config)
    all_models = discover_models(all_engines)

    for ek, model_ids in all_models.items():
        merge_discovered_models(ek, model_ids)

    if model_name is None:
        model_name = config.intelligence.default_model

    if not model_name:
        engine_models = all_models.get(engine_name, [])
        if engine_models:
            model_name = engine_models[0]

    if not model_name:
        model_name = config.intelligence.fallback_model

    if not model_name:
        console.print("[red]No model available.[/red]")
        sys.exit(1)

    if not user_set_max_tokens:
        suggested = adjust_tokens_for_model(
            complexity_result.suggested_max_tokens,
            model_name,
        )
        max_tokens = max(suggested, config.intelligence.max_tokens)

    if agent_name is not None:
        parsed_tools = resolve_tool_names(
            tool_names,
            getattr(config.tools, "enabled", None),
            getattr(config.agent, "tools", None),
        )

        result = _run_agent(
            agent_name,
            query_text,
            engine,
            model_name,
            parsed_tools,
            config,
            bus,
            temperature,
            max_tokens,
            capability_policy=sec.capability_policy,
        )

        click.echo(
            json_mod.dumps({"content": result.content}, indent=2)
            if output_json else result.content
        )
        return

    lena = _get_lena_kernel(engine, model_name)
    result = lena.run([{"role": "user", "content": query_text}])

    content = (
        result.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )

    if not content:
        console.print("[red]No response generated.[/red]")
        sys.exit(1)

    click.echo(content)

    if enable_profile:
        _print_profile(
            bus,
            time.monotonic() - wall_start,
            engine_name,
            model_name,
            console,
            complexity_result=complexity_result,
        )

    if telem_store is not None:
        try:
            telem_store.close()
        except Exception:
            pass