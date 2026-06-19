from __future__ import annotations

from proc_py.ctx import Ctx
from proc_py.loader import load_fns


def main() -> None:
    ctx = load_fns(Ctx(config={"currency": "USD"}), "invoice_bot_fns")
    print(getattr(ctx.fns, "system_start")(ctx))


if __name__ == "__main__":
    main()
