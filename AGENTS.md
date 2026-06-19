# Agent Notes

This repository is an experimental Python runtime inspired by
`niquola/proc-ts`.

## Architecture Rules

- Keep one public procedure per file.
- Pass `ctx` explicitly as the first argument.
- Call procedure dependencies through `ctx.fns`, not direct imports.
- Keep I/O explicit at procedure boundaries.
- Put reusable runtime behavior in `proc_py/`.
- Keep examples small and runnable.

## Verification

Before calling a change done, run:

```bash
uv run --extra dev pytest -q
uv run --extra dev --with pyright pyright
PYTHONPATH=examples/repo_digest:. python3 examples/repo_digest/run_digest.py
```

The REPL `eval` path is a local development tool. Do not present it as a
security boundary.
