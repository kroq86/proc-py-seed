from __future__ import annotations

from proc_py.ctx import Ctx


def hello(ctx: Ctx, name: str = "world") -> str:
    prefix = ctx.config.get("prefix", "hello")
    return f"{prefix}, {name}"
