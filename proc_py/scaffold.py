from __future__ import annotations

from pathlib import Path


def create_proc_file(name: str, fns_dir: str | Path = "proc_py/fns") -> Path:
    """Create a one-function procedure module."""

    if not name.isidentifier() or name.startswith("_"):
        raise RuntimeError(f"procedure name must be a public Python identifier: {name}")

    path = Path(fns_dir) / f"{name}.py"
    if path.exists():
        raise RuntimeError(f"procedure already exists: {path}")

    path.write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "",
                "from proc_py.ctx import Ctx",
                "",
                "",
                f"def {name}(ctx: Ctx) -> str:",
                f'    return "{name}"',
                "",
            ]
        )
    )
    return path
