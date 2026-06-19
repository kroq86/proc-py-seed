from __future__ import annotations

from proc_py.ctx import Ctx


def calculate_totals(ctx: Ctx, orders: list[dict[str, int | str]]) -> dict[str, int]:
    total = sum(int(order["amount"]) for order in orders)
    return {"count": len(orders), "total": total}
