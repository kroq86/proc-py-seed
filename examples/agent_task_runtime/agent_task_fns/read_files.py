from __future__ import annotations

from pathlib import Path

from agent_task_fns._ctx_types import AgentTaskCtx


def read_files(ctx: AgentTaskCtx, files: list[str]) -> dict[str, str]:
    root = Path(str(ctx.config.get("root", ".")))
    max_chars = int(ctx.config.get("max_file_chars", 4000))
    result: dict[str, str] = {}
    for file_name in files:
        path = root / file_name
        try:
            result[file_name] = path.read_text(encoding="utf-8")[:max_chars]
        except UnicodeDecodeError:
            result[file_name] = "<binary or non-utf8 file>"
    ctx.state["file_text"] = result
    return result
