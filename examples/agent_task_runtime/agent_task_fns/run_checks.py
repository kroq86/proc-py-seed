from __future__ import annotations

from subprocess import run
from time import perf_counter
from typing import cast

from agent_task_fns._ctx_types import AgentTaskCtx
from agent_task_fns._state import CheckResult


def run_checks(ctx: AgentTaskCtx) -> CheckResult:
    raw_command = cast(object, ctx.config.get("test_command", ["python3", "-m", "pytest", "-q"]))
    if not isinstance(raw_command, list):
        raise RuntimeError("test_command must be a list of strings")
    raw_parts = cast(list[object], raw_command)
    if not all(isinstance(part, str) for part in raw_parts):
        raise RuntimeError("test_command must be a list of strings")
    command = cast(list[str], raw_parts)

    start = perf_counter()
    completed = run(command, capture_output=True, text=True, timeout=30, check=False)
    result: CheckResult = {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "seconds": round(perf_counter() - start, 3),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    ctx.state["last_checks"] = result
    return result
