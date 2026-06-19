from __future__ import annotations

from json import loads
from pathlib import Path
from typing import cast

from agent_task_fns._ctx_types import AgentTaskCtx


def detect_project_checks(ctx: AgentTaskCtx) -> list[str]:
    root = Path(str(ctx.config.get("root", ".")))
    checks: list[str] = []

    package_json = root / "package.json"
    if package_json.exists():
        scripts = _package_scripts(package_json)
        for name in ("typecheck", "test", "build"):
            if name in scripts:
                checks.append(f"npm run {name}")

    cargo_toml = root / "Cargo.toml"
    if cargo_toml.exists():
        checks.extend(["cargo test", "cargo check"])

    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        checks.append("uv run --extra dev pytest -q")
        checks.append("uv run --extra dev --with pyright pyright")

    if not checks:
        checks.append("No standard checks detected")

    ctx.state["detected_checks"] = checks
    return checks


def _package_scripts(path: Path) -> dict[str, object]:
    try:
        data = loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return {}
    if not isinstance(data, dict):
        return {}
    package = cast(dict[str, object], data)
    scripts = package.get("scripts", {})
    if not isinstance(scripts, dict):
        return {}
    result: dict[str, object] = {}
    for key, value in cast(dict[object, object], scripts).items():
        if isinstance(key, str):
            result[key] = value
    return result
