from __future__ import annotations

from typing import Any, Protocol

class RepoDigestFns(Protocol):
    """Generated registry protocol for procedures loaded into ctx.fns."""

    def collect_todos(self, ctx: RepoDigestCtx, files: list[str]) -> 'list[dict[str, int | str]]': ...
    def render_report(self, ctx: RepoDigestCtx, files: list[str], todos: 'list[dict[str, int | str]]') -> str: ...
    def scan_files(self, ctx: RepoDigestCtx) -> list[str]: ...
    def summarize_tests(self, ctx: RepoDigestCtx) -> 'dict[str, int | str | bool | float]': ...
    def system_start(self, ctx: RepoDigestCtx) -> str: ...


class RepoDigestCtx(Protocol):
    """Generated context protocol with app-specific ctx.fns typing."""

    fns: RepoDigestFns
    config: dict[str, Any]
    state: dict[str, Any]
    t: Any
