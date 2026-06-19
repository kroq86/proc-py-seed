from __future__ import annotations

from agent_task_fns._ctx_types import AgentTaskCtx


def summarize_checks(ctx: AgentTaskCtx, result: dict[str, bool | int | float | str]) -> str:
    output = f"{result.get('stdout', '')}{result.get('stderr', '')}".strip()
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    summary = next(
        (
            line
            for line in reversed(lines)
            if " passed" in line or " failed" in line or " error" in line
        ),
        lines[-1] if lines else "no check output",
    )
    status = "passed" if result.get("ok") is True else "failed"
    text = f"{status}: {summary} ({result.get('seconds')}s)"
    ctx.state["check_summary"] = text
    return text
