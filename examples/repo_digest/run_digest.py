from __future__ import annotations

from typing import cast

from proc_py.ctx import Ctx
from proc_py.loader import load_fns
from repo_digest_fns._ctx_types import RepoDigestCtx


def main() -> None:
    ctx = cast(
        RepoDigestCtx,
        load_fns(
            Ctx(
                config={
                    "root": ".",
                    "test_command": ["uv", "run", "--extra", "dev", "pytest", "-q"],
                }
            ),
            "repo_digest_fns",
        ),
    )
    print(ctx.fns.system_start(ctx))


if __name__ == "__main__":
    main()
