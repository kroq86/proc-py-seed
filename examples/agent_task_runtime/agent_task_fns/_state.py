from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, cast

if TYPE_CHECKING:
    from agent_task_fns._ctx_types import AgentTaskCtx


class RepoInfo(TypedDict):
    files: list[str]
    python_files: list[str]
    test_files: list[str]


class CheckResult(TypedDict):
    ok: bool
    returncode: int
    seconds: float
    stdout: str
    stderr: str


def repo_info(ctx: AgentTaskCtx) -> RepoInfo:
    value = ctx.state.get("repo")
    if not isinstance(value, dict):
        raise RuntimeError("repo state is missing; call inspect_repo first")
    repo = cast(dict[str, object], value)
    return {
        "files": _string_list(repo.get("files", [])),
        "python_files": _string_list(repo.get("python_files", [])),
        "test_files": _string_list(repo.get("test_files", [])),
    }


def relevant_files(ctx: AgentTaskCtx) -> list[str]:
    return _string_list(ctx.state.get("relevant_files", []))


def file_text(ctx: AgentTaskCtx) -> dict[str, str]:
    value = ctx.state.get("file_text", {})
    if not isinstance(value, dict):
        return {}
    result: dict[str, str] = {}
    for key, item in cast(dict[object, object], value).items():
        if isinstance(key, str) and isinstance(item, str):
            result[key] = item
    return result


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in cast(list[object], value):
        if isinstance(item, str):
            result.append(item)
    return result
