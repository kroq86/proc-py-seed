from __future__ import annotations

from pathlib import Path

from agent_task_fns._ctx_types import AgentTaskCtx
from agent_task_fns._state import RepoInfo


def inspect_repo(ctx: AgentTaskCtx) -> RepoInfo:
    root = Path(str(ctx.config.get("root", ".")))
    excluded = {".git", ".venv", ".pytest_cache", "__pycache__"}
    files: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in excluded for part in path.parts):
            continue
        files.append(path.relative_to(root).as_posix())

    python_files = [file_name for file_name in files if file_name.endswith(".py")]
    test_files = [file_name for file_name in python_files if "test" in Path(file_name).name]
    repo: RepoInfo = {
        "files": sorted(files),
        "python_files": sorted(python_files),
        "test_files": sorted(test_files),
    }
    ctx.state["repo"] = repo
    return repo
