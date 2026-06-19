from __future__ import annotations

from pathlib import Path

from agent_task_fns._ctx_types import AgentTaskCtx
from agent_task_fns._state import repo_info


def find_relevant_files(ctx: AgentTaskCtx, task: str) -> list[str]:
    files = repo_info(ctx)["files"]
    root = Path(str(ctx.config.get("root", ".")))

    terms = {
        token.strip(".,:;()[]{}").lower()
        for token in task.replace("_", " ").replace("-", " ").split()
        if len(token.strip(".,:;()[]{}")) >= 4
    }
    scored: list[tuple[int, str]] = []
    for file_name in files:
        haystack = file_name.replace("_", " ").replace("-", " ").lower()
        score = sum(1 for term in terms if term in haystack)
        score += _content_score(root / file_name, terms)
        if file_name.endswith(".py") and any(part in file_name for part in ("proc_py", "examples")):
            score += 1
        if Path(file_name).name in {"README.md", "pyproject.toml"}:
            score += 1
        if score:
            scored.append((score, file_name))

    relevant = [file_name for _, file_name in sorted(scored, reverse=True)[:8]]
    ctx.state["relevant_files"] = relevant
    return relevant


def _content_score(path: Path, terms: set[str]) -> int:
    if path.suffix not in {".py", ".md", ".toml"}:
        return 0
    try:
        text = path.read_text(encoding="utf-8")[:3000].lower()
    except UnicodeDecodeError:
        return 0
    return min(3, sum(1 for term in terms if term in text))
