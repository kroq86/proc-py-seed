from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from proc_py.ctx import Ctx


class CtxFns(Protocol):
    """Generated registry protocol for procedures loaded into ctx.fns."""

    def hello(self, ctx: Ctx, name: str = 'world') -> str: ...
    def system_start(self, ctx: Ctx) -> str: ...
