from __future__ import annotations

from agent_task_fns._ctx_types import AgentTaskCtx
from agent_task_fns._state import relevant_files


def render_next_actions(ctx: AgentTaskCtx) -> list[str]:
    files = relevant_files(ctx)
    actions = [
        "Review the proposed patch plan before editing files.",
        "Open the top relevant files and confirm they match the task.",
    ]
    if files:
        actions.append(f"Start with `{files[0]}`.")
    actions.extend(
        [
            "Make the smallest focused code change.",
            "Regenerate app-local ctx.fns types if procedure signatures changed.",
            "Run pytest, Pyright, and the dogfood workflow again.",
        ]
    )
    ctx.state["next_actions"] = actions
    return actions
