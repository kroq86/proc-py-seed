from __future__ import annotations

from repo_digest_fns._ctx_types import RepoDigestCtx


def render_report(
    ctx: RepoDigestCtx, files: list[str], todos: list[dict[str, int | str]]
) -> str:
    tests = ctx.state.get("tests", {})
    py_files = [file_name for file_name in files if file_name.endswith(".py")]
    lines = [
        "# Repo Digest",
        "",
        f"- files scanned: {len(files)}",
        f"- Python files: {len(py_files)}",
        f"- TODO/FIXME/HACK matches: {len(todos)}",
        f"- tests: {tests.get('summary', 'not run')}",
        f"- test duration: {tests.get('seconds', 'n/a')}s",
        "",
        "## Notable TODOs",
        "",
    ]
    if todos:
        for item in todos[:10]:
            lines.append(f"- `{item['file']}:{item['line']}` {item['text']}")
    else:
        lines.append("- none")
    return "\n".join(lines)
