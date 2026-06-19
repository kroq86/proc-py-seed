from __future__ import annotations

from agent_task_fns._ctx_types import AgentTaskCtx
from agent_task_fns._state import CheckResult


def summarize_checks(ctx: AgentTaskCtx, result: CheckResult) -> str:
    output = f"{result['stdout']}{result['stderr']}".strip()
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    summary = next(
        (
            line
            for line in reversed(lines)
            if " passed" in line or " failed" in line or " error" in line
        ),
        lines[-1] if lines else "no check output",
    )
    status = "passed" if result["ok"] else "failed"
    text = f"{status}: {summary} ({result['seconds']}s)"
    ctx.state["check_summary"] = text
    return text
