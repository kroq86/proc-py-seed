from __future__ import annotations

from pathlib import Path

from repo_digest_fns._ctx_types import RepoDigestCtx


def scan_files(ctx: RepoDigestCtx) -> list[str]:
    root = Path(str(ctx.config.get("root", ".")))
    excluded = {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
    }
    files: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in excluded for part in path.parts):
            continue
        files.append(path.relative_to(root).as_posix())
    return sorted(files)
