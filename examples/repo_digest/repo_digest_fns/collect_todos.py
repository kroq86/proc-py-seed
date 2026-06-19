from __future__ import annotations

from pathlib import Path

from repo_digest_fns._ctx_types import RepoDigestCtx


def collect_todos(ctx: RepoDigestCtx, files: list[str]) -> list[dict[str, int | str]]:
    root = Path(str(ctx.config.get("root", ".")))
    prefixes = ("# TODO:", "# FIXME:", "# HACK:", "// TODO:", "// FIXME:", "// HACK:")
    matches: list[dict[str, int | str]] = []
    for file_name in files:
        path = root / file_name
        if path.suffix not in {".md", ".py", ".toml", ".txt"}:
            continue
        try:
            with path.open("r", encoding="utf-8") as handle:
                for line_number, line in enumerate(handle, start=1):
                    if line.lstrip().startswith(prefixes):
                        matches.append(
                            {
                                "file": file_name,
                                "line": line_number,
                                "text": line.strip(),
                            }
                        )
        except UnicodeDecodeError:
            continue
    return matches
