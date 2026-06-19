from __future__ import annotations

from typing import Any

from proc_py.ctx import Ctx
from proc_py.loader import load_fns


def create_ctx(config: dict[str, Any] | None = None) -> Ctx:
    ctx = Ctx(config=dict(config or {}))
    return load_fns(ctx)
