from __future__ import annotations

from agent_task_fns._ctx_types import AgentTaskCtx


def system_start(ctx: AgentTaskCtx, task: str) -> str:
    clean_task = ctx.fns.set_task(ctx, task)
    ctx.fns.inspect_repo(ctx)
    relevant = ctx.fns.find_relevant_files(ctx, clean_task)
    ctx.fns.read_files(ctx, relevant)
    checks = ctx.fns.run_checks(ctx)
    ctx.fns.summarize_checks(ctx, checks)
    ctx.t = {"task": clean_task, "relevant_files": relevant}
    return ctx.fns.render_pr_description(ctx)
