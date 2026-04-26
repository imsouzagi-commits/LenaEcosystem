from __future__ import annotations

import asyncio
import importlib
import json
import logging
import re
from contextlib import nullcontext
from pathlib import Path
from typing import Any, Optional

import click
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table

from openjarvis.evals.core.display import (
    print_banner,
    print_completion,
    print_full_results,
    print_run_header,
    print_section,
    print_subject_table,
    print_suite_summary,
)

LOGGER = logging.getLogger(__name__)


BENCHMARKS: dict[str, dict[str, str]] = {
    "supergpqa": {"category": "reasoning", "description": "SuperGPQA multiple-choice"},
    "gpqa": {"category": "reasoning", "description": "GPQA graduate-level MCQ"},
    "mmlu-pro": {"category": "reasoning", "description": "MMLU-Pro multiple-choice"},
    "math500": {"category": "reasoning", "description": "MATH-500 math problems"},
    "natural-reasoning": {"category": "reasoning", "description": "Natural Reasoning"},
    "hle": {"category": "reasoning", "description": "HLE hard challenges"},
    "simpleqa": {"category": "chat", "description": "SimpleQA factual QA"},
    "wildchat": {"category": "chat", "description": "WildChat conversation quality"},
    "ipw": {"category": "chat", "description": "IPW mixed benchmark"},
    "gaia": {"category": "agentic", "description": "GAIA agentic benchmark"},
    "frames": {"category": "rag", "description": "FRAMES multi-hop RAG"},
    "swebench": {"category": "agentic", "description": "SWE-bench code patches"},
    "swefficiency": {"category": "agentic", "description": "SWEfficiency optimization"},
    "terminalbench": {"category": "agentic", "description": "TerminalBench terminal tasks"},
    "terminalbench-native": {"category": "agentic", "description": "TerminalBench Native (Docker)"},
    "email_triage": {"category": "use-case", "description": "Email triage classification + draft"},
    "morning_brief": {"category": "use-case", "description": "Morning briefing generation"},
    "research_mining": {"category": "use-case", "description": "Research synthesis + accuracy"},
    "knowledge_base": {"category": "use-case", "description": "Document-grounded retrieval QA"},
    "coding_task": {"category": "use-case", "description": "Function-level code generation"},
    "loghub": {"category": "agentic", "description": "LogHub log anomaly detection"},
    "ama-bench": {"category": "agentic", "description": "AMA-Bench agent memory assessment"},
    "lifelong-agent": {"category": "agentic", "description": "LifelongAgentBench sequential task learning"},
    "deepplanning": {"category": "agentic", "description": "DeepPlanning shopping constraints"},
    "paperarena": {"category": "agentic", "description": "PaperArena paper analysis"},
    "webchorearena": {"category": "agentic", "description": "WebChoreArena web chore tasks"},
    "workarena": {"category": "agentic", "description": "WorkArena++ enterprise workflows"},
    "coding_assistant": {"category": "use-case", "description": "Bug-fix coding assistant"},
    "security_scanner": {"category": "use-case", "description": "Security vulnerability scanner"},
    "daily_digest": {"category": "use-case", "description": "Daily briefing generation"},
    "doc_qa": {"category": "use-case", "description": "Document-grounded QA"},
    "browser_assistant": {"category": "use-case", "description": "Web research with fact verification"},
    "pinchbench": {"category": "agentic", "description": "PinchBench real-world agent tasks"},
    "taubench": {"category": "agentic", "description": "TauBench customer service"},
    "livecodebench": {"category": "coding", "description": "LiveCodeBench"},
    "liveresearch": {"category": "agentic", "description": "DeepResearchBench"},
    "deepresearch": {"category": "agentic", "description": "DeepResearchBench alias"},
    "liveresearchbench": {"category": "reasoning", "description": "LiveResearchBench Salesforce"},
    "toolcall15": {"category": "agentic", "description": "ToolCall-15"},
}

BACKENDS = {
    "jarvis-direct": "Engine-level inference",
    "jarvis-agent": "Agent-level inference",
}

DATASET_REGISTRY = {
    "supergpqa": ("openjarvis.evals.datasets.supergpqa", "SuperGPQADataset"),
    "gpqa": ("openjarvis.evals.datasets.gpqa", "GPQADataset"),
    "mmlu-pro": ("openjarvis.evals.datasets.mmlu_pro", "MMLUProDataset"),
    "math500": ("openjarvis.evals.datasets.math500", "MATH500Dataset"),
    "natural-reasoning": ("openjarvis.evals.datasets.natural_reasoning", "NaturalReasoningDataset"),
    "hle": ("openjarvis.evals.datasets.hle", "HLEDataset"),
    "simpleqa": ("openjarvis.evals.datasets.simpleqa", "SimpleQADataset"),
    "wildchat": ("openjarvis.evals.datasets.wildchat", "WildChatDataset"),
    "ipw": ("openjarvis.evals.datasets.ipw_mixed", "IPWDataset"),
    "gaia": ("openjarvis.evals.datasets.gaia", "GAIADataset"),
    "frames": ("openjarvis.evals.datasets.frames", "FRAMESDataset"),
    "swebench": ("openjarvis.evals.datasets.swebench", "SWEBenchDataset"),
    "swefficiency": ("openjarvis.evals.datasets.swefficiency", "SWEfficiencyDataset"),
    "terminalbench": ("openjarvis.evals.datasets.terminalbench", "TerminalBenchDataset"),
    "terminalbench-native": ("openjarvis.evals.datasets.terminalbench_native", "TerminalBenchNativeDataset"),
    "email_triage": ("openjarvis.evals.datasets.email_triage", "EmailTriageDataset"),
    "morning_brief": ("openjarvis.evals.datasets.morning_brief", "MorningBriefDataset"),
    "research_mining": ("openjarvis.evals.datasets.research_mining", "ResearchMiningDataset"),
    "knowledge_base": ("openjarvis.evals.datasets.knowledge_base", "KnowledgeBaseDataset"),
    "coding_task": ("openjarvis.evals.datasets.coding_task", "CodingTaskDataset"),
    "loghub": ("openjarvis.evals.datasets.loghub", "LogHubDataset"),
    "ama-bench": ("openjarvis.evals.datasets.ama_bench", "AMABenchDataset"),
    "lifelong-agent": ("openjarvis.evals.datasets.lifelong_agent", "LifelongAgentDataset"),
    "deepplanning": ("openjarvis.evals.datasets.deepplanning", "DeepPlanningDataset"),
    "paperarena": ("openjarvis.evals.datasets.paperarena", "PaperArenaDataset"),
    "webchorearena": ("openjarvis.evals.datasets.webchorearena", "WebChoreArenaDataset"),
    "workarena": ("openjarvis.evals.datasets.workarena", "WorkArenaDataset"),
    "coding_assistant": ("openjarvis.evals.datasets.coding_assistant", "CodingAssistantDataset"),
    "security_scanner": ("openjarvis.evals.datasets.security_scanner", "SecurityScannerDataset"),
    "daily_digest": ("openjarvis.evals.datasets.daily_digest", "DailyDigestDataset"),
    "doc_qa": ("openjarvis.evals.datasets.doc_qa", "DocQADataset"),
    "browser_assistant": ("openjarvis.evals.datasets.browser_assistant", "BrowserAssistantDataset"),
    "pinchbench": ("openjarvis.evals.datasets.pinchbench", "PinchBenchDataset"),
    "taubench": ("openjarvis.evals.datasets.taubench", "TauBenchDataset"),
    "livecodebench": ("openjarvis.evals.datasets.livecodebench", "LiveCodeBenchDataset"),
    "liveresearch": ("openjarvis.evals.datasets.liveresearch", "LiveResearchBenchDataset"),
    "deepresearch": ("openjarvis.evals.datasets.liveresearch", "LiveResearchBenchDataset"),
    "liveresearchbench": ("openjarvis.evals.datasets.liveresearchbench", "LiveResearchBenchSFDataset"),
    "toolcall15": ("openjarvis.evals.datasets.toolcall15", "ToolCall15Dataset"),
}

SCORER_REGISTRY = {
    "supergpqa": ("openjarvis.evals.scorers.supergpqa_mcq", "SuperGPQAScorer"),
    "gpqa": ("openjarvis.evals.scorers.gpqa_mcq", "GPQAScorer"),
    "mmlu-pro": ("openjarvis.evals.scorers.mmlu_pro_mcq", "MMLUProScorer"),
    "math500": ("openjarvis.evals.scorers.reasoning_judge", "ReasoningJudgeScorer"),
    "natural-reasoning": ("openjarvis.evals.scorers.reasoning_judge", "ReasoningJudgeScorer"),
    "hle": ("openjarvis.evals.scorers.hle_judge", "HLEScorer"),
    "simpleqa": ("openjarvis.evals.scorers.simpleqa_judge", "SimpleQAScorer"),
    "wildchat": ("openjarvis.evals.scorers.wildchat_judge", "WildChatScorer"),
    "ipw": ("openjarvis.evals.scorers.ipw_mixed", "IPWMixedScorer"),
    "gaia": ("openjarvis.evals.scorers.gaia_exact", "GAIAScorer"),
    "frames": ("openjarvis.evals.scorers.frames_judge", "FRAMESScorer"),
    "swebench": ("openjarvis.evals.scorers.swebench_structural", "SWEBenchScorer"),
    "swefficiency": ("openjarvis.evals.scorers.swefficiency_structural", "SWEfficiencyScorer"),
    "terminalbench": ("openjarvis.evals.scorers.terminalbench_judge", "TerminalBenchScorer"),
    "terminalbench-native": ("openjarvis.evals.scorers.terminalbench_native_structural", "TerminalBenchNativeScorer"),
    "email_triage": ("openjarvis.evals.scorers.email_triage", "EmailTriageScorer"),
    "morning_brief": ("openjarvis.evals.scorers.morning_brief", "MorningBriefScorer"),
    "research_mining": ("openjarvis.evals.scorers.research_mining", "ResearchMiningScorer"),
    "knowledge_base": ("openjarvis.evals.scorers.knowledge_base", "KnowledgeBaseScorer"),
    "coding_task": ("openjarvis.evals.scorers.coding_task", "CodingTaskScorer"),
    "loghub": ("openjarvis.evals.scorers.loghub_scorer", "LogHubScorer"),
    "ama-bench": ("openjarvis.evals.scorers.ama_bench_judge", "AMABenchScorer"),
    "lifelong-agent": ("openjarvis.evals.scorers.lifelong_agent_scorer", "LifelongAgentScorer"),
    "deepplanning": ("openjarvis.evals.scorers.deepplanning_scorer", "DeepPlanningScorer"),
    "paperarena": ("openjarvis.evals.scorers.paperarena_judge", "PaperArenaScorer"),
    "webchorearena": ("openjarvis.evals.scorers.webchorearena_scorer", "WebChoreArenaScorer"),
    "workarena": ("openjarvis.evals.scorers.workarena_scorer", "WorkArenaScorer"),
    "coding_assistant": ("openjarvis.evals.scorers.coding_assistant", "CodingAssistantScorer"),
    "security_scanner": ("openjarvis.evals.scorers.security_scanner", "SecurityScannerScorer"),
    "daily_digest": ("openjarvis.evals.scorers.daily_digest", "DailyDigestScorer"),
    "doc_qa": ("openjarvis.evals.scorers.doc_qa", "DocQAScorer"),
    "browser_assistant": ("openjarvis.evals.scorers.browser_assistant", "BrowserAssistantScorer"),
    "pinchbench": ("openjarvis.evals.scorers.pinchbench", "PinchBenchScorer"),
    "taubench": ("openjarvis.evals.scorers.taubench", "TauBenchScorer"),
    "livecodebench": ("openjarvis.evals.scorers.livecodebench", "LiveCodeBenchScorer"),
    "liveresearch": ("openjarvis.evals.scorers.liveresearch", "LiveResearchBenchScorer"),
    "deepresearch": ("openjarvis.evals.scorers.liveresearch", "LiveResearchBenchScorer"),
    "liveresearchbench": ("openjarvis.evals.scorers.liveresearchbench", "LiveResearchBenchSFScorer"),
    "toolcall15": ("openjarvis.evals.scorers.toolcall15", "ToolCall15Scorer"),
}


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _dynamic_import(module_name: str, class_name: str) -> Any:
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def _build_backend(backend_name: str, engine_key: Optional[str], agent_name: str, tools: list[str], telemetry: bool = False, gpu_metrics: bool = False, model: Optional[str] = None, max_turns: Optional[int] = None):
    if backend_name == "jarvis-agent":
        from openjarvis.evals.backends.jarvis_agent import JarvisAgentBackend
        return JarvisAgentBackend(engine_key=engine_key, agent_name=agent_name, tools=tools, telemetry=telemetry, gpu_metrics=gpu_metrics, model=model, max_turns=max_turns)

    from openjarvis.evals.backends.jarvis_direct import JarvisDirectBackend
    return JarvisDirectBackend(engine_key=engine_key, telemetry=telemetry, gpu_metrics=gpu_metrics)


def _build_dataset(name: str, subset: str | None = None):
    if name not in DATASET_REGISTRY:
        raise click.ClickException(f"Unknown benchmark dataset: {name}")

    module_name, class_name = DATASET_REGISTRY[name]
    cls = _dynamic_import(module_name, class_name)

    if name == "lifelong-agent":
        return cls(subset=subset or "db_bench")
    if name == "pinchbench":
        return cls(path=subset)
    if name == "taubench":
        return cls(domains=subset.split(",") if subset else None)
    if name in {"liveresearch", "deepresearch"}:
        return cls(path=subset)

    return cls()


def _build_scorer(name: str, judge_backend, judge_model: str):
    if name not in SCORER_REGISTRY:
        raise click.ClickException(f"Unknown benchmark scorer: {name}")

    module_name, class_name = SCORER_REGISTRY[name]
    cls = _dynamic_import(module_name, class_name)
    return cls(judge_backend, judge_model)


def _build_judge_backend(judge_model: str, engine_key: str = "cloud"):
    from openjarvis.evals.backends.jarvis_direct import JarvisDirectBackend
    try:
        return JarvisDirectBackend(engine_key=engine_key)
    except RuntimeError as exc:
        LOGGER.warning("Judge backend unavailable: %s", exc)
        return None


def _safe_close(resource: Any) -> None:
    if resource is not None and hasattr(resource, "close"):
        try:
            resource.close()
        except Exception as exc:
            LOGGER.debug("Close failed: %s", exc)


def _run_terminalbench_native(config, console: Console):
    from openjarvis.evals.backends.terminalbench_native import TerminalBenchNativeBackend
    from openjarvis.evals.core.types import RunSummary

    litellm_model = f"openai/{config.model}"
    output_dir = getattr(config, "output_path", None) or "results/terminalbench-native/"
    backend = TerminalBenchNativeBackend(
        model=litellm_model,
        api_base="http://localhost:8000/v1",
        temperature=config.temperature,
        max_samples=config.max_samples,
        output_dir=output_dir,
        n_concurrent=config.max_workers or 4,
    )

    model_slug = re.sub(r"[^a-z0-9_-]", "-", config.model.lower().replace("/", "-"))
    run_id = f"tb2-{model_slug}"
    console.print(f"  Running TerminalBench Native: {config.model}")
    results = backend.run_harness(run_id)

    total = len(getattr(results, "trial_results", []))
    correct = sum(1 for tr in getattr(results, "trial_results", []) if getattr(tr, "is_resolved", False))
    accuracy = correct / total if total else 0.0

    return RunSummary(
        benchmark="terminalbench-native",
        category="agentic",
        backend="terminalbench-native",
        model=config.model,
        total_samples=total,
        scored_samples=total,
        correct=correct,
        accuracy=accuracy,
        errors=0,
        mean_latency_seconds=0.0,
        total_cost_usd=0.0,
    )


def _execute_standard_eval(config, console: Console):
    from openjarvis.evals.core.runner import EvalRunner

    eval_backend = None
    judge_backend = None

    try:
        if config.benchmark == "terminalbench-native":
            return _run_terminalbench_native(config, console)

        eval_backend = _build_backend(
            config.backend,
            config.engine_key,
            config.agent_name or "orchestrator",
            config.tools,
            telemetry=config.telemetry,
            gpu_metrics=config.gpu_metrics,
            model=config.model,
        )

        dataset = _build_dataset(config.benchmark, getattr(config, "dataset_subset", None))

        if hasattr(dataset, "set_engine_config"):
            dataset.set_engine_config(
                engine_key=config.engine_key,
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                telemetry=config.telemetry,
                gpu_metrics=config.gpu_metrics,
            )

        judge_backend = _build_judge_backend(config.judge_model, config.judge_engine)
        scorer = _build_scorer(config.benchmark, judge_backend, config.judge_model)
        runner = EvalRunner(config, dataset, eval_backend, scorer)

        if config.max_samples and config.max_samples > 0:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Evaluating...", total=config.max_samples)
                return runner.run(progress_callback=lambda done, total: progress.update(task, completed=done))

        with console.status("Evaluating samples..."):
            return runner.run()

    finally:
        _safe_close(eval_backend)
        _safe_close(judge_backend)


@click.group()
def main():
    """OpenJarvis Evaluation Framework."""


@main.command()
@click.option("-b", "--benchmark", default=None, type=click.Choice(list(BENCHMARKS.keys())))
@click.option("--backend", default="jarvis-direct", type=click.Choice(list(BACKENDS.keys())))
@click.option("-m", "--model", default=None)
@click.option("-e", "--engine", "engine_key", default=None)
@click.option("--agent", "agent_name", default="orchestrator")
@click.option("--tools", default="")
@click.option("-n", "--max-samples", type=int, default=None)
@click.option("-w", "--max-workers", type=int, default=4)
@click.option("--judge-model", default="gpt-5-mini-2025-08-07")
@click.option("--judge-engine", default="cloud")
@click.option("-o", "--output", "output_path", default=None)
@click.option("--seed", type=int, default=42)
@click.option("--split", "dataset_split", default=None)
@click.option("--temperature", type=float, default=0.0)
@click.option("--max-tokens", type=int, default=2048)
@click.option("--telemetry/--no-telemetry", default=False)
@click.option("--gpu-metrics/--no-gpu-metrics", default=False)
@click.option("-v", "--verbose", is_flag=True)
def run(
    benchmark,
    backend,
    model,
    engine_key,
    agent_name,
    tools,
    max_samples,
    max_workers,
    judge_model,
    judge_engine,
    output_path,
    seed,
    dataset_split,
    temperature,
    max_tokens,
    telemetry,
    gpu_metrics,
    verbose,
):
    _setup_logging(verbose)

    if not benchmark:
        raise click.UsageError("Missing --benchmark")
    if not model:
        raise click.UsageError("Missing --model")

    from openjarvis.evals.core.types import RunConfig

    config = RunConfig(
        benchmark=benchmark,
        backend=backend,
        model=model,
        max_samples=max_samples,
        max_workers=max_workers,
        judge_model=judge_model,
        judge_engine=judge_engine,
        engine_key=engine_key,
        agent_name=agent_name,
        tools=[t.strip() for t in tools.split(",") if t.strip()],
        output_path=output_path,
        seed=seed,
        dataset_split=dataset_split,
        temperature=temperature,
        max_tokens=max_tokens,
        telemetry=telemetry,
        gpu_metrics=gpu_metrics,
    )

    console = Console()
    print_banner(console)
    print_section(console, "Configuration")
    print_run_header(console, benchmark=benchmark, model=model, backend=backend, samples=max_samples, workers=max_workers)

    print_section(console, "Evaluation")
    summary = _execute_standard_eval(config, console)

    print_section(console, "Results")
    print_full_results(console, summary)
    if summary.per_subject and len(summary.per_subject) > 1:
        print_subject_table(console, summary.per_subject)
    print_completion(console, summary, getattr(summary, "_output_path", None), getattr(summary, "_traces_dir", None))


@main.command("run-all")
@click.option("-m", "--model", required=True)
@click.option("-e", "--engine", "engine_key", default=None)
@click.option("-n", "--max-samples", type=int, default=None)
@click.option("-w", "--max-workers", type=int, default=4)
@click.option("--judge-model", default="gpt-5-mini-2025-08-07")
@click.option("--output-dir", default="results/")
@click.option("--seed", type=int, default=42)
@click.option("-v", "--verbose", is_flag=True)
def run_all(model, engine_key, max_samples, max_workers, judge_model, output_dir, seed, verbose):
    _setup_logging(verbose)
    from openjarvis.evals.core.types import RunConfig

    console = Console()
    print_banner(console)

    summaries = []
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    for idx, benchmark in enumerate(BENCHMARKS.keys(), 1):
        print_section(console, f"Run {idx}/{len(BENCHMARKS)}: {benchmark}")

        config = RunConfig(
            benchmark=benchmark,
            backend="jarvis-direct",
            model=model,
            max_samples=max_samples,
            max_workers=max_workers,
            judge_model=judge_model,
            engine_key=engine_key,
            output_path=str(output_dir_path / f"{benchmark}_{model.replace('/', '-').replace(':', '-')}.jsonl"),
            seed=seed,
        )

        try:
            summary = _execute_standard_eval(config, console)
            summaries.append(summary)
            console.print(f"  [green]{summary.accuracy:.4f}[/green] ({summary.correct}/{summary.scored_samples})")
        except Exception as exc:
            console.print(f"  [red]FAILED[/red] {exc}")

    if summaries:
        print_section(console, "Suite Results")
        print_suite_summary(console, summaries, f"All Benchmarks / {model}")


@main.command()
@click.argument("jsonl_path", type=click.Path(exists=True))
def summarize(jsonl_path):
    records = [json.loads(line) for line in Path(jsonl_path).read_text().splitlines() if line.strip()]
    if not records:
        click.echo("No records found.")
        return

    scored = [r for r in records if r.get("is_correct") is not None]
    correct = [r for r in scored if r["is_correct"]]
    errors = [r for r in records if r.get("error")]
    accuracy = len(correct) / len(scored) if scored else 0.0

    console = Console()
    console.print(f"[cyan]File:[/cyan] {jsonl_path}")
    console.print(f"[cyan]Benchmark:[/cyan] {records[0].get('benchmark', '?')}")
    console.print(f"[cyan]Model:[/cyan] {records[0].get('model', '?')}")
    console.print(f"[cyan]Total:[/cyan] {len(records)}")
    console.print(f"[cyan]Scored:[/cyan] {len(scored)}")
    console.print(f"[cyan]Correct:[/cyan] {len(correct)}")
    console.print(f"[cyan]Accuracy:[/cyan] [bold]{accuracy:.4f}[/bold]")
    console.print(f"[cyan]Errors:[/cyan] {len(errors)}")


@main.command("list")
def list_cmd():
    console = Console()
    print_banner(console)

    bench_table = Table(title="Available Benchmarks", border_style="bright_blue")
    bench_table.add_column("Name", style="cyan")
    bench_table.add_column("Category")
    bench_table.add_column("Description")
    for name, info in BENCHMARKS.items():
        bench_table.add_row(name, info["category"], info["description"])
    console.print(bench_table)

    backend_table = Table(title="Available Backends", border_style="bright_blue")
    backend_table.add_column("Name", style="cyan")
    backend_table.add_column("Description")
    for name, desc in BACKENDS.items():
        backend_table.add_row(name, desc)
    console.print(backend_table)


if __name__ == "__main__":
    main()