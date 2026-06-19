from __future__ import annotations

from agent_task_fns._ctx_types import AgentTaskCtx


def set_task(ctx: AgentTaskCtx, task: str) -> str:
    clean_task = task.strip()
    if not clean_task:
        raise RuntimeError("task must not be empty")
    ctx.state["task"] = clean_task
    return clean_task
