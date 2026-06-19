from __future__ import annotations

from proc_py.ctx import Ctx


def system_start(ctx: Ctx) -> str:
    orders = getattr(ctx.fns, "load_orders")(ctx)
    totals = getattr(ctx.fns, "calculate_totals")(ctx, orders)
    ctx.state["last_totals"] = totals
    ctx.t = orders[0]
    return getattr(ctx.fns, "render_digest")(ctx, totals)
