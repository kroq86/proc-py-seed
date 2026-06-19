from __future__ import annotations

from pathlib import Path
from typing import cast

from agent_task_fns._ctx_types import AgentTaskCtx


def find_relevant_files(ctx: AgentTaskCtx, task: str) -> list[str]:
    repo = cast(object, ctx.state.get("repo", {}))
    if not isinstance(repo, dict):
        raise RuntimeError("repo state is missing; call inspect_repo first")
    repo_data = cast(dict[str, object], repo)
    raw_files = repo_data.get("files", [])
    if not isinstance(raw_files, list):
        raise RuntimeError("repo files are missing; call inspect_repo first")
    files: list[str] = []
    raw_file_items = cast(list[object], raw_files)
    for item in raw_file_items:
        if isinstance(item, str):
            files.append(item)

    terms = {
        token.strip(".,:;()[]{}").lower()
        for token in task.replace("_", " ").replace("-", " ").split()
        if len(token.strip(".,:;()[]{}")) >= 4
    }
    scored: list[tuple[int, str]] = []
    for file_name in files:
        haystack = file_name.replace("_", " ").replace("-", " ").lower()
        score = sum(1 for term in terms if term in haystack)
        if file_name.endswith(".py") and any(part in file_name for part in ("proc_py", "examples")):
            score += 1
        if Path(file_name).name in {"README.md", "pyproject.toml"}:
            score += 1
        if score:
            scored.append((score, file_name))

    relevant = [file_name for _, file_name in sorted(scored, reverse=True)[:8]]
    ctx.state["relevant_files"] = relevant
    return relevant
