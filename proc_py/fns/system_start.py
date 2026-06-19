from __future__ import annotations

from proc_py.ctx import Ctx


def system_start(ctx: Ctx) -> str:
    return ctx.fns.hello(ctx, "agent")
