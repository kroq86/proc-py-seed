# Agent Task Runtime Example

Dogfood example for using `proc-py` as a tiny agent task runtime.

Run from the repo root:

```bash
PYTHONPATH=examples/agent_task_runtime:. python3 examples/agent_task_runtime/run_agent_task.py \
  "add reload support to the loader"
```

The example does not call an LLM. It models the procedural runtime an agent
could use:

- store the task in `ctx.state`;
- inspect the repository;
- find relevant files with a simple heuristic;
- read bounded file context;
- run checks;
- summarize check output;
- render a PR-style description.

Regenerate app-local typing:

```bash
PYTHONPATH=examples/agent_task_runtime:. python3 -m proc_py.cli generate-types \
  --package agent_task_fns \
  --output examples/agent_task_runtime/agent_task_fns/_ctx_types.py \
  --protocol-name AgentTaskFns \
  --ctx-protocol-name AgentTaskCtx
```
