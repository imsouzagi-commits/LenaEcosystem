# LENA DEPENDENCY GRAPH

```text
Gerado em: 2026-04-29T10:44:48
Escopo: ecossistema Lena solicitado
Arquivos no escopo detectados: 51
Método: AST imports + leitura estática; não altera código.
```

## 1. Arquivos Que Importam LenaAgent Diretamente

```text
- src/openjarvis/cli/main.py:3 -> from openjarvis.agent.lena_agent import LenaAgent [CLI/entrypoint real]
- src/openjarvis/cli/serve.py:10 -> from openjarvis.agent.lena_agent import LenaAgent [CLI/entrypoint real]
- src/openjarvis/cli/voice_cli.py:3 -> from openjarvis.agent.lena_agent import LenaAgent [CLI/entrypoint real]
- tests/agent/test_lena_agent.py:4 -> from openjarvis.agent.lena_agent import LenaAgent [teste/harness, não fluxo de produção]
- tests/lena_acceptance_extreme.py:8 -> from openjarvis.agent.lena_agent import LenaAgent [teste/harness, não fluxo de produção]
- tests/lena_master_validation_v13.py:10 -> from openjarvis.agent.lena_agent import LenaAgent [teste/harness, não fluxo de produção]
- tests/lena_ultimate_monster_test.py:8 -> from openjarvis.agent.lena_agent import LenaAgent [teste/harness, não fluxo de produção]
- tests/lena_ultimate_monster_test_v2.py:10 -> from openjarvis.agent.lena_agent import LenaAgent [teste/harness, não fluxo de produção]
- tests/tests/lena_ultimate_monster_test_v3.py:7 -> from openjarvis.agent.lena_agent import LenaAgent [teste/harness, não fluxo de produção]
```

## 2. Arquivos Que Importam LenaKernel Diretamente

```text
- src/openjarvis/agent/lena_agent.py:24 -> from openjarvis.lena.kernel import LenaKernel [biblioteca Lena; executado quando importado/chamado por entrypoint]
- src/openjarvis/cli/ask.py:26 -> from openjarvis.lena.kernel import LenaKernel [CLI/entrypoint real]
- src/openjarvis/lena/browser_executor.py:8 -> from openjarvis.lena.kernel import LenaKernel [biblioteca Lena; executado quando importado/chamado por entrypoint]
```

## 3. Arquivos Que Importam conversation_router.chat

```text
nenhum import direto de chat detectado no escopo
```

## 4. Arquivos Que Importam LenaActionCenter / LenaCommandCenter

```text
- src/openjarvis/brain/conversation_router.py:11 -> from openjarvis.lena.action_center import LenaActionCenter [pipeline alternativo; só executado se alguém importar chat]
- src/openjarvis/lena/action_center.py:6 -> from openjarvis.lena.command_center import LenaCommandCenter [biblioteca Lena; executado quando importado/chamado por entrypoint]
```

## 5. Arquivos Que Importam memory.manager Ou LenaMemoryEngine

```text
- src/openjarvis/agent/lena_memory_engine.py:6 -> from openjarvis.memory.manager import MemoryManager [biblioteca Lena; executado quando importado/chamado por entrypoint]
- src/openjarvis/brain/conversation_router.py:12 -> from openjarvis.memory.manager import memory [pipeline alternativo; só executado se alguém importar chat]
```

## 6. Grafo Interno Entre Módulos src/openjarvis/lena/*

```text
- src/openjarvis/lena/__init__.py -> sem imports internos Lena
- src/openjarvis/lena/action_center.py:6 -> src/openjarvis/lena/command_center.py (from openjarvis.lena.command_center import LenaCommandCenter)
- src/openjarvis/lena/action_guard.py:3 -> src/openjarvis/lena/audit_log_center.py (from openjarvis.lena.audit_log_center import LenaAuditLogCenter)
- src/openjarvis/lena/action_guard.py:4 -> src/openjarvis/lena/safety_center.py (from openjarvis.lena.safety_center import LenaSafetyCenter)
- src/openjarvis/lena/app_registry.py -> sem imports internos Lena
- src/openjarvis/lena/audit_log_center.py:3 -> src/openjarvis/lena/persistent_store.py (from openjarvis.lena.persistent_store import LenaPersistentStore)
- src/openjarvis/lena/boot_logger.py:3 -> src/openjarvis/lena/persistent_store.py (from openjarvis.lena.persistent_store import LenaPersistentStore)
- src/openjarvis/lena/browser_executor.py:6 -> src/openjarvis/lena/action_guard.py (from openjarvis.lena.action_guard import LenaActionGuard)
- src/openjarvis/lena/browser_executor.py:7 -> src/openjarvis/lena/job_center.py (from openjarvis.lena.job_center import LenaJobCenter)
- src/openjarvis/lena/browser_executor.py:8 -> src/openjarvis/lena/kernel.py (from openjarvis.lena.kernel import LenaKernel)
- src/openjarvis/lena/browser_intent.py -> sem imports internos Lena
- src/openjarvis/lena/command_center.py -> sem imports internos Lena
- src/openjarvis/lena/diagnostics_center.py -> sem imports internos Lena
- src/openjarvis/lena/file_operator.py:6 -> src/openjarvis/lena/action_guard.py (from openjarvis.lena.action_guard import LenaActionGuard)
- src/openjarvis/lena/file_operator.py:7 -> src/openjarvis/lena/job_center.py (from openjarvis.lena.job_center import LenaJobCenter)
- src/openjarvis/lena/file_operator.py:8 -> src/openjarvis/lena/workspace_center.py (from openjarvis.lena.workspace_center import LenaWorkspaceCenter)
- src/openjarvis/lena/job_center.py:6 -> src/openjarvis/lena/persistent_store.py (from openjarvis.lena.persistent_store import LenaPersistentStore)
- src/openjarvis/lena/kernel.py:10 -> src/openjarvis/lena/boot_logger.py (from openjarvis.lena.boot_logger import LenaBootLogger)
- src/openjarvis/lena/kernel.py:16 -> src/openjarvis/lena/kernel_watchdog.py (from openjarvis.lena.kernel_watchdog import LenaKernelWatchdog)
- src/openjarvis/lena/kernel.py:11 -> src/openjarvis/lena/permission_center.py (from openjarvis.lena.permission_center import LenaPermissionCenter)
- src/openjarvis/lena/kernel.py:12 -> src/openjarvis/lena/service_registry.py (from openjarvis.lena.service_registry import LenaServiceRegistry)
- src/openjarvis/lena/kernel.py:13 -> src/openjarvis/lena/state_center.py (from openjarvis.lena.state_center import HealthStatus, LenaGlobalState)
- src/openjarvis/lena/kernel.py:14 -> src/openjarvis/lena/workspace_center.py (from openjarvis.lena.workspace_center import LenaWorkspaceCenter)
- src/openjarvis/lena/kernel.py:15 -> src/openjarvis/lena/workspace_indexer.py (from openjarvis.lena.workspace_indexer import LenaWorkspaceIndexer)
- src/openjarvis/lena/kernel_watchdog.py:6 -> src/openjarvis/lena/boot_logger.py (from openjarvis.lena.boot_logger import LenaBootLogger)
- src/openjarvis/lena/kernel_watchdog.py:7 -> src/openjarvis/lena/page_bridge.py (from openjarvis.lena.page_bridge import LenaPageBridge)
- src/openjarvis/lena/kernel_watchdog.py:8 -> src/openjarvis/lena/workspace_indexer.py (from openjarvis.lena.workspace_indexer import LenaWorkspaceIndexer)
- src/openjarvis/lena/memory_center.py -> sem imports internos Lena
- src/openjarvis/lena/memory_persistence.py:7 -> src/openjarvis/lena/workspace_center.py (from openjarvis.lena.workspace_center import LenaWorkspaceCenter)
- src/openjarvis/lena/page_bridge.py:7 -> src/openjarvis/lena/workspace_center.py (from openjarvis.lena.workspace_center import LenaWorkspaceCenter)
- src/openjarvis/lena/permission_center.py -> sem imports internos Lena
- src/openjarvis/lena/persistent_store.py:8 -> src/openjarvis/lena/workspace_center.py (from openjarvis.lena.workspace_center import LenaWorkspaceCenter)
- src/openjarvis/lena/persona_center.py -> sem imports internos Lena
- src/openjarvis/lena/runtime_guard.py -> sem imports internos Lena
- src/openjarvis/lena/safety_center.py -> sem imports internos Lena
- src/openjarvis/lena/service_registry.py -> sem imports internos Lena
- src/openjarvis/lena/state_center.py -> sem imports internos Lena
- src/openjarvis/lena/task_context.py -> sem imports internos Lena
- src/openjarvis/lena/task_orchestrator.py -> sem imports internos Lena
- src/openjarvis/lena/temporal_center.py -> sem imports internos Lena
- src/openjarvis/lena/workspace_center.py -> sem imports internos Lena
- src/openjarvis/lena/workspace_indexer.py:5 -> src/openjarvis/lena/workspace_center.py (from openjarvis.lena.workspace_center import LenaWorkspaceCenter)
```

## 7. Imports Mortos Vs Executados Por CLI Real

```text
Provavelmente executados por CLI/servidor real:
- src/openjarvis/cli/ask.py: Comando jarvis ask real, mas import/API LenaKernel parece quebrado
- src/openjarvis/cli/main.py: CLI interativo simples real se invocado como módulo/script
- src/openjarvis/cli/serve.py: Servidor FastAPI alternativo real se usado como openjarvis.cli.serve
- src/openjarvis/cli/voice_cli.py: CLI voz real/manual, mas assinatura LenaAgent parece quebrada

Executados transitivamente por LenaAgent em cli/main.py ou cli/serve.py:
- src/openjarvis/agent/lena_agent.py: importado pelos entrypoints cli/main.py e cli/serve.py
- src/openjarvis/agent/lena_fast_brain.py: import direto de lena_agent.py
- src/openjarvis/agent/lena_response_mutator.py: import direto de lena_agent.py
- src/openjarvis/agent/lena_social_dynamics.py: import direto de lena_agent.py
- src/openjarvis/agent/lena_social_engine.py: import direto de lena_agent.py
- src/openjarvis/lena/action_guard.py: usado por lena_agent.py, browser_executor.py e file_operator.py
- src/openjarvis/lena/app_registry.py: import direto de lena_agent.py
- src/openjarvis/lena/audit_log_center.py: usado via action_guard.py
- src/openjarvis/lena/boot_logger.py: usado via kernel.py/kernel_watchdog.py
- src/openjarvis/lena/browser_executor.py: import direto de lena_agent.py
- src/openjarvis/lena/browser_intent.py: import direto de lena_agent.py
- src/openjarvis/lena/diagnostics_center.py: import direto de lena_agent.py
- src/openjarvis/lena/file_operator.py: import direto de lena_agent.py
- src/openjarvis/lena/job_center.py: import direto de lena_agent.py e usado por executores
- src/openjarvis/lena/kernel.py: import direto de lena_agent.py
- src/openjarvis/lena/kernel_watchdog.py: usado via kernel.py
- src/openjarvis/lena/memory_persistence.py: usado pela classe LenaMemoryEngine interna de lena_agent.py
- src/openjarvis/lena/page_bridge.py: import direto de lena_agent.py e usado por watchdog
- src/openjarvis/lena/permission_center.py: usado via kernel.py
- src/openjarvis/lena/persistent_store.py: usado por audit/job/boot logs
- src/openjarvis/lena/runtime_guard.py: import direto de lena_agent.py
- src/openjarvis/lena/safety_center.py: usado via action_guard.py
- src/openjarvis/lena/service_registry.py: usado via kernel.py
- src/openjarvis/lena/state_center.py: usado via kernel.py
- src/openjarvis/lena/task_context.py: import direto de lena_agent.py
- src/openjarvis/lena/task_orchestrator.py: import direto de lena_agent.py
- src/openjarvis/lena/workspace_center.py: usado por kernel, persistence, file/page/logs
- src/openjarvis/lena/workspace_indexer.py: usado via kernel.py/kernel_watchdog.py

Executados apenas pelo pipeline alternativo conversation_router, não pelo LenaAgent atual:
- src/openjarvis/brain/conversation_router.py
- src/openjarvis/lena/action_center.py
- src/openjarvis/lena/command_center.py
- src/openjarvis/memory/manager.py

Provavelmente mortos/órfãos no fluxo principal atual:
- src/openjarvis/agent/lena_memory_engine.py: sem import interno direto detectado no escopo
- src/openjarvis/agent/lena_state.py: sem import interno direto detectado no escopo
- src/openjarvis/brain/conversation_router.py: sem import interno direto detectado no escopo
- src/openjarvis/lena/__init__.py: sem import interno direto detectado no escopo
- src/openjarvis/lena/memory_center.py: sem import interno direto detectado no escopo
- src/openjarvis/lena/persona_center.py: sem import interno direto detectado no escopo
- src/openjarvis/lena/temporal_center.py: sem import interno direto detectado no escopo
- src/openjarvis/memory/extractor.py: sem import interno direto detectado no escopo

Observação: arquivos podem ser usados dinamicamente por registry/entrypoint externo não capturado por AST.
```

## 8. Tabela De Dependência

| Arquivo | Importa dentro do ecossistema Lena | Importado por | Status | Risco se remover |
|---|---|---|---|---|
| `src/openjarvis/agent/lena_agent.py` | `src/openjarvis/agent/lena_fast_brain.py`, `src/openjarvis/agent/lena_response_mutator.py`, `src/openjarvis/agent/lena_social_dynamics.py`, `src/openjarvis/agent/lena_social_engine.py`, `src/openjarvis/lena/action_guard.py`, `src/openjarvis/lena/app_registry.py`, `src/openjarvis/lena/browser_executor.py`, `src/openjarvis/lena/browser_intent.py`, `src/openjarvis/lena/diagnostics_center.py`, `src/openjarvis/lena/file_operator.py`, `src/openjarvis/lena/job_center.py`, `src/openjarvis/lena/kernel.py`, `src/openjarvis/lena/memory_persistence.py`, `src/openjarvis/lena/page_bridge.py`, `src/openjarvis/lena/runtime_guard.py`, `src/openjarvis/lena/task_context.py`, `src/openjarvis/lena/task_orchestrator.py` | `src/openjarvis/cli/main.py`, `src/openjarvis/cli/serve.py`, `src/openjarvis/cli/voice_cli.py`, `tests/agent/test_lena_agent.py`, `tests/lena_acceptance_extreme.py`, `tests/lena_master_validation_v13.py`, `tests/lena_ultimate_monster_test.py`, `tests/lena_ultimate_monster_test_v2.py`, `tests/tests/lena_ultimate_monster_test_v3.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/agent/lena_fast_brain.py` | - | `src/openjarvis/agent/lena_agent.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/agent/lena_memory_engine.py` | `src/openjarvis/memory/manager.py` | - | biblioteca Lena; executado quando importado/chamado por entrypoint | baixo/médio, verificar uso dinâmico |
| `src/openjarvis/agent/lena_response_mutator.py` | `src/openjarvis/agent/lena_social_engine.py` | `src/openjarvis/agent/lena_agent.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/agent/lena_social_dynamics.py` | - | `src/openjarvis/agent/lena_agent.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/agent/lena_social_engine.py` | - | `src/openjarvis/agent/lena_agent.py`, `src/openjarvis/agent/lena_response_mutator.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/agent/lena_state.py` | - | - | biblioteca Lena; executado quando importado/chamado por entrypoint | baixo/médio, verificar uso dinâmico |
| `src/openjarvis/brain/conversation_router.py` | `src/openjarvis/lena/action_center.py`, `src/openjarvis/memory/manager.py` | - | pipeline alternativo; só executado se alguém importar chat | baixo/médio, verificar uso dinâmico |
| `src/openjarvis/cli/ask.py` | `src/openjarvis/lena/kernel.py` | - | CLI/entrypoint real | médio/alto |
| `src/openjarvis/cli/main.py` | `src/openjarvis/agent/lena_agent.py` | - | CLI/entrypoint real | médio/alto |
| `src/openjarvis/cli/serve.py` | `src/openjarvis/agent/lena_agent.py` | - | CLI/entrypoint real | médio/alto |
| `src/openjarvis/cli/voice_cli.py` | `src/openjarvis/agent/lena_agent.py` | - | CLI/entrypoint real | médio/alto |
| `src/openjarvis/lena/__init__.py` | - | - | biblioteca Lena; executado quando importado/chamado por entrypoint | baixo/médio, verificar uso dinâmico |
| `src/openjarvis/lena/action_center.py` | `src/openjarvis/lena/command_center.py` | `src/openjarvis/brain/conversation_router.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/action_guard.py` | `src/openjarvis/lena/audit_log_center.py`, `src/openjarvis/lena/safety_center.py` | `src/openjarvis/agent/lena_agent.py`, `src/openjarvis/lena/browser_executor.py`, `src/openjarvis/lena/file_operator.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/app_registry.py` | - | `src/openjarvis/agent/lena_agent.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/audit_log_center.py` | `src/openjarvis/lena/persistent_store.py` | `src/openjarvis/lena/action_guard.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/boot_logger.py` | `src/openjarvis/lena/persistent_store.py` | `src/openjarvis/lena/kernel.py`, `src/openjarvis/lena/kernel_watchdog.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/browser_executor.py` | `src/openjarvis/lena/action_guard.py`, `src/openjarvis/lena/job_center.py`, `src/openjarvis/lena/kernel.py` | `src/openjarvis/agent/lena_agent.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/browser_intent.py` | - | `src/openjarvis/agent/lena_agent.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/command_center.py` | - | `src/openjarvis/lena/action_center.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/diagnostics_center.py` | - | `src/openjarvis/agent/lena_agent.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/file_operator.py` | `src/openjarvis/lena/action_guard.py`, `src/openjarvis/lena/job_center.py`, `src/openjarvis/lena/workspace_center.py` | `src/openjarvis/agent/lena_agent.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/job_center.py` | `src/openjarvis/lena/persistent_store.py` | `src/openjarvis/agent/lena_agent.py`, `src/openjarvis/lena/browser_executor.py`, `src/openjarvis/lena/file_operator.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/kernel.py` | `src/openjarvis/lena/boot_logger.py`, `src/openjarvis/lena/kernel_watchdog.py`, `src/openjarvis/lena/permission_center.py`, `src/openjarvis/lena/service_registry.py`, `src/openjarvis/lena/state_center.py`, `src/openjarvis/lena/workspace_center.py`, `src/openjarvis/lena/workspace_indexer.py` | `src/openjarvis/agent/lena_agent.py`, `src/openjarvis/cli/ask.py`, `src/openjarvis/lena/browser_executor.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/kernel_watchdog.py` | `src/openjarvis/lena/boot_logger.py`, `src/openjarvis/lena/page_bridge.py`, `src/openjarvis/lena/workspace_indexer.py` | `src/openjarvis/lena/kernel.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/memory_center.py` | - | - | biblioteca Lena; executado quando importado/chamado por entrypoint | baixo/médio, verificar uso dinâmico |
| `src/openjarvis/lena/memory_persistence.py` | `src/openjarvis/lena/workspace_center.py` | `src/openjarvis/agent/lena_agent.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/page_bridge.py` | `src/openjarvis/lena/workspace_center.py` | `src/openjarvis/agent/lena_agent.py`, `src/openjarvis/lena/kernel_watchdog.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/permission_center.py` | - | `src/openjarvis/lena/kernel.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/persistent_store.py` | `src/openjarvis/lena/workspace_center.py` | `src/openjarvis/lena/audit_log_center.py`, `src/openjarvis/lena/boot_logger.py`, `src/openjarvis/lena/job_center.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/persona_center.py` | - | - | biblioteca Lena; executado quando importado/chamado por entrypoint | baixo/médio, verificar uso dinâmico |
| `src/openjarvis/lena/runtime_guard.py` | - | `src/openjarvis/agent/lena_agent.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/safety_center.py` | - | `src/openjarvis/lena/action_guard.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/service_registry.py` | - | `src/openjarvis/lena/kernel.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/state_center.py` | - | `src/openjarvis/lena/kernel.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/task_context.py` | - | `src/openjarvis/agent/lena_agent.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/task_orchestrator.py` | - | `src/openjarvis/agent/lena_agent.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/temporal_center.py` | - | - | biblioteca Lena; executado quando importado/chamado por entrypoint | baixo/médio, verificar uso dinâmico |
| `src/openjarvis/lena/workspace_center.py` | - | `src/openjarvis/lena/file_operator.py`, `src/openjarvis/lena/kernel.py`, `src/openjarvis/lena/memory_persistence.py`, `src/openjarvis/lena/page_bridge.py`, `src/openjarvis/lena/persistent_store.py`, `src/openjarvis/lena/workspace_indexer.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/lena/workspace_indexer.py` | `src/openjarvis/lena/workspace_center.py` | `src/openjarvis/lena/kernel.py`, `src/openjarvis/lena/kernel_watchdog.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `src/openjarvis/memory/extractor.py` | - | - | biblioteca Lena; executado quando importado/chamado por entrypoint | baixo/médio, verificar uso dinâmico |
| `src/openjarvis/memory/manager.py` | - | `src/openjarvis/agent/lena_memory_engine.py`, `src/openjarvis/brain/conversation_router.py` | biblioteca Lena; executado quando importado/chamado por entrypoint | médio/alto |
| `tests/agent/test_lena_agent.py` | `src/openjarvis/agent/lena_agent.py` | - | teste/harness, não fluxo de produção | baixo para runtime; médio para cobertura |
| `tests/lena_acceptance_extreme.py` | `src/openjarvis/agent/lena_agent.py` | - | teste/harness, não fluxo de produção | baixo para runtime; médio para cobertura |
| `tests/lena_e2e_runner.py` | - | - | teste/harness, não fluxo de produção | baixo para runtime; médio para cobertura |
| `tests/lena_master_validation_v13.py` | `src/openjarvis/agent/lena_agent.py` | - | teste/harness, não fluxo de produção | baixo para runtime; médio para cobertura |
| `tests/lena_score_report.py` | - | - | teste/harness, não fluxo de produção | baixo para runtime; médio para cobertura |
| `tests/lena_ultimate_monster_test.py` | `src/openjarvis/agent/lena_agent.py` | - | teste/harness, não fluxo de produção | baixo para runtime; médio para cobertura |
| `tests/lena_ultimate_monster_test_v2.py` | `src/openjarvis/agent/lena_agent.py` | - | teste/harness, não fluxo de produção | baixo para runtime; médio para cobertura |
| `tests/tests/lena_ultimate_monster_test_v3.py` | `src/openjarvis/agent/lena_agent.py` | - | teste/harness, não fluxo de produção | baixo para runtime; médio para cobertura |

## 9. Árvore De Chamadas

```text
Fluxo A - CLI main/serve usando LenaAgent:
  cli/main.py::main
    -> LenaAgent()
      -> LenaKernel()
        -> thread bootstrap
          -> LenaWorkspaceCenter.bootstrap
          -> LenaPermissionCenter.probe
          -> LenaWorkspaceIndexer.build_index
          -> LenaKernelWatchdog.start
            -> loop: _refresh_health + build_index + LenaPageBridge.publish
      -> LenaSocialEngine / LenaSocialDynamics / LenaResponseMutator / LenaFastBrain / LenaMemoryEngine interno
    -> LenaAgent.run(messages)
      -> _extract_user_text
      -> _classify_route
        -> LenaFastBrain.can_answer
        -> LenaBrowserIntent.is_search_intent
      -> LenaTaskOrchestrator.execute(..., _execute_single_intent)
        -> _execute_single_intent
          -> FAST_BRAIN: LenaFastBrain.answer
          -> WEB_OPEN: _open_url -> LenaActionGuard.allow -> LenaAuditLogCenter -> LenaPersistentStore.write_audit; LenaJobCenter -> subprocess open
          -> DESKTOP: _execute_desktop_commands -> _hard_open_app/_hard_close_app -> subprocess open/osascript/pkill + LenaJobCenter
          -> MEMORY_SUMMARY: LenaMemoryEngine interno + LenaDiagnosticsCenter/LenaPageBridge
          -> WEB_SEARCH: LenaBrowserExecutor.search -> subprocess open Atlas + LenaJobCenter
          -> FILE_OP: LenaFileOperator create/read/delete/move/list
      -> social_engine.analyze
      -> response_mutator.mutate
      -> social_dynamics.update_after_turn
      -> memory_engine.push_exchange -> LenaMemoryPersistence.save

Fluxo B - conversation_router alternativo:
  conversation_router.chat(messages)
    -> memory.manager.memory.absorb
    -> se comando local: LenaActionCenter.try_execute
      -> LenaCommandCenter.parse
      -> MacDesktopController.open_multiple_apps/close_multiple_apps ou webbrowser.open
    -> se pergunta factual: _memory_response(memory.manager.memory)
    -> senão: _cloud_response
      -> HeuristicRouter.select_model
      -> CloudEngine.generate
      -> _refine_response

Fluxo C - cli/ask.py pretendido:
  ask(...)
    -> _get_lena_kernel(engine, model_name)
      -> LenaKernel(engine=..., model=...)  [incompatível com assinatura atual]
    -> lena.run(...) [LenaKernel não define run]
```

## 10. Pontos Perigosos Ao Remover Arquivos Órfãos

```text
1. src/openjarvis/lena/action_center.py parece órfão para LenaAgent, mas é usado por brain/conversation_router.py. Remover quebra esse pipeline alternativo.
2. src/openjarvis/lena/command_center.py é dependência direta de action_center.py. Remover isoladamente quebra ActionCenter.
3. src/openjarvis/agent/lena_memory_engine.py parece não usado pelo LenaAgent atual, mas testes/fluxos antigos podem esperar essa API. Remover exige busca em histórico/docs.
4. src/openjarvis/lena/memory_center.py parece não estar no fluxo principal, mas pode representar refactor planejado. Remover pode descartar lógica de memória mais completa.
5. src/openjarvis/memory/manager.py tem singleton global. Mesmo com poucos imports, pode ter efeitos colaterais no import.
6. Arquivos tests/lena_* são harnesses manuais/e2e. Remover não afeta runtime, mas elimina validação de comportamento desktop/conversacional.
7. cli/ask.py importa LenaKernel e está provavelmente quebrado hoje; corrigir antes de remover qualquer kernel/module para não mascarar erro de contrato.
8. Muitos módulos Lena são acionados por chamada indireta, não por import direto do usuário. Remover arquivo sem seguir call tree quebra runtime mesmo se parecer pequeno.
```

## 11. Diagnóstico Final Do Grafo

```text
- O grafo tem dois centros concorrentes: LenaAgent e conversation_router.chat.
- LenaKernel é tratado como runtime/lifecycle por LenaAgent, mas cli/ask.py tenta tratá-lo como agente executável.
- ActionCenter/CommandCenter pertencem ao pipeline conversation_router, não ao fluxo principal de LenaAgent.
- memory.manager pertence ao conversation_router e agent/lena_memory_engine.py; LenaAgent atual usa classe interna e LenaMemoryPersistence.
- lena/memory_center.py é um terceiro sistema de memória com baixo acoplamento atual.
- Remoção segura exige primeiro escolher o fluxo canônico: LenaAgent ou conversation_router.
```
