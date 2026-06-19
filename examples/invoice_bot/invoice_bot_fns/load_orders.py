from __future__ import annotations

from proc_py.ctx import Ctx


def load_orders(ctx: Ctx) -> list[dict[str, int | str]]:
    return [
        {"customer": "Ada", "amount": 120},
        {"customer": "Grace", "amount": 90},
    ]
