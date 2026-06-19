from __future__ import annotations

from sys import argv
from typing import cast

from agent_task_fns._ctx_types import AgentTaskCtx
from proc_py.ctx import Ctx
from proc_py.loader import load_fns


def main() -> None:
    task = " ".join(argv[1:]) or "inspect this repository"
    ctx = cast(
        AgentTaskCtx,
        load_fns(
            Ctx(
                config={
                    "root": ".",
                    "test_command": ["uv", "run", "--extra", "dev", "pytest", "-q"],
                    "max_file_chars": 4000,
                    "ollama_model": "qwen2.5-coder:1.5b",
                    "ollama_timeout": 60,
                }
            ),
            "agent_task_fns",
        ),
    )
    print(ctx.fns.system_start(ctx, task))


if __name__ == "__main__":
    main()
