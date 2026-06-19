# Agent Task Runtime Example

Dogfood example for using `proc-py` as a tiny agent task runtime.

Run from the repo root:

```bash
PYTHONPATH=examples/agent_task_runtime:. python3 examples/agent_task_runtime/run_agent_task.py \
  "add reload support to the loader"
```

The example models the procedural runtime a coding agent could use:

- store the task in `ctx.state`;
- inspect the repository;
- find relevant files with a simple heuristic;
- read bounded file context;
- run checks;
- summarize check output;
- render a PR-style description.

If local Ollama is available, the workflow also asks the configured model to
draft the PR description. The default model is `qwen2.5-coder:1.5b` for quick
local feedback. If Ollama is unavailable or times out, the report falls back to
the deterministic description.

Regenerate app-local typing:

```bash
PYTHONPATH=examples/agent_task_runtime:. python3 -m proc_py.cli generate-types \
  --package agent_task_fns \
  --output examples/agent_task_runtime/agent_task_fns/_ctx_types.py \
  --protocol-name AgentTaskFns \
  --ctx-protocol-name AgentTaskCtx
```
