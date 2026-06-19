from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, Callable, cast

from proc_py.ctx_fns import CtxFns

ProcFn = Callable[..., Any]


@dataclass(slots=True)
class Ctx:
    """Runtime context passed explicitly to every procedure."""

    fns: CtxFns = field(default_factory=lambda: cast(CtxFns, SimpleNamespace()))
    config: dict[str, Any] = field(default_factory=lambda: {})
    state: dict[str, Any] = field(default_factory=lambda: {})
    t: Any = None

    def register(self, name: str, fn: ProcFn) -> None:
        setattr(self.fns, name, fn)
