from __future__ import annotations

from repo_digest_fns._ctx_types import RepoDigestCtx


def system_start(ctx: RepoDigestCtx) -> str:
    files = ctx.fns.scan_files(ctx)
    todos = ctx.fns.collect_todos(ctx, files)
    ctx.state["tests"] = ctx.fns.summarize_tests(ctx)
    ctx.t = {"files": files[:5], "todos": todos[:3]}
    return ctx.fns.render_report(ctx, files, todos)
