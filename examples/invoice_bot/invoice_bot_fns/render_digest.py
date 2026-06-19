from __future__ import annotations

from proc_py.ctx import Ctx


def render_digest(ctx: Ctx, totals: dict[str, int]) -> str:
    currency = ctx.config.get("currency", "USD")
    return f"{totals['count']} invoices, {totals['total']} {currency}"
