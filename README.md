# proc-py-seed

Experimental procedural Python runtime for agent-friendly automation:
**one function per file, explicit `ctx`, reloadable `ctx.fns`, REPL-friendly
workflow, and generated Pyright typing.**

`proc-py-seed` is inspired by
[`niquola/proc-ts`](https://github.com/niquola/proc-ts), but it is not a
TypeScript port. It asks a narrower Python question:

> Can a small Python system stay easy to inspect, edit, reload, and type-check
> when it is built from procedures and explicit runtime state instead of
> classes, DI containers, decorators, and framework magic?

Status: **experimental alpha**. Useful as a research seed and dogfoodable
automation runtime. Not a production framework.

## Why This Exists

Most Python tools start simple and then drift into hidden state:

```text
scripts -> imports -> globals -> services -> framework glue -> restart cycle
```

This project keeps the moving parts visible:

```text
ctx lives
functions live in files
functions call dependencies through ctx.fns
edit one file
reload one function
call it again
```

That shape is especially friendly to coding agents and REPL-style development:
an agent can read a 30-line procedure, change it, reload it, call it, and see
the result without walking a class hierarchy.

## Core Ideas

- **One public procedure per file**: `hello.py` exports `hello(ctx, ...)`.
- **Explicit context**: every procedure receives `ctx` as the first argument.
- **Late-bound dependencies**: procedures call each other through `ctx.fns`.
- **Reload without stale imports**: `reload_fn(ctx, "hello")` replaces
  `ctx.fns.hello` in the live context.
- **Runtime state is visible**: `ctx.state` is durable runtime data; `ctx.t` is
  scratch space for REPL/debugging.
- **Generated typing**: `ctx.fns` gets a generated `Protocol` with real
  procedure signatures.

## Install / Run From Source

This seed uses no runtime dependencies. For development, use `uv`:

```bash
uv run --extra dev pytest -q
uv run --extra dev --with pyright pyright
```

Try the CLI:

```bash
uv run python -m proc_py.cli list
uv run python -m proc_py.cli call hello Ada
uv run python -m proc_py.cli new-fn calculate_price
uv run python -m proc_py.cli generate-types
```

If installed as a package, the console script is:

```bash
proc-py list
proc-py call hello Ada
```

## Procedure Shape

Every procedure lives in `proc_py/fns/<name>.py` and exports one public callable
with the same name:

```python
from __future__ import annotations

from proc_py.ctx import Ctx


def hello(ctx: Ctx, name: str = "world") -> str:
    prefix = ctx.config.get("prefix", "hello")
    return f"{prefix}, {name}"
```

Procedures call dependencies through `ctx.fns`:

```python
from __future__ import annotations

from proc_py.ctx import Ctx


def system_start(ctx: Ctx) -> str:
    return ctx.fns.hello(ctx, "agent")
```

Avoid direct procedure-to-procedure imports. Direct imports can keep stale
function references after reload.

## REPL Workflow

Start the local development REPL server:

```bash
uv run python -m proc_py.cli repl
```

In another terminal:

```bash
uv run python -m proc_py.cli send eval 'hello(ctx, "Ada")'
```

Edit `proc_py/fns/hello.py`, then reload only that function:

```bash
uv run python -m proc_py.cli send reload hello
uv run python -m proc_py.cli send eval 'hello(ctx, "Ada")'
```

The same `ctx` stays alive in the REPL process. `ctx.state` and `ctx.t` survive
function reloads.

Security note: REPL `eval` is a local development tool, not a sandbox and not a
security boundary.

## Generated Typing

For the default package:

```bash
uv run python -m proc_py.cli generate-types
```

This generates `proc_py/ctx_fns.py` with real procedure signatures:

```python
class CtxFns(Protocol):
    def hello(self, ctx: Ctx, name: str = "world") -> str: ...
    def system_start(self, ctx: Ctx) -> str: ...
```

For a custom procedure package, generate app-local types:

```bash
PYTHONPATH=examples/repo_digest:. python3 -m proc_py.cli generate-types \
  --package repo_digest_fns \
  --output examples/repo_digest/repo_digest_fns/_ctx_types.py \
  --protocol-name RepoDigestFns \
  --ctx-protocol-name RepoDigestCtx
```

Then procedures can use direct typed dispatch:

```python
from repo_digest_fns._ctx_types import RepoDigestCtx


def system_start(ctx: RepoDigestCtx) -> str:
    files = ctx.fns.scan_files(ctx)
    todos = ctx.fns.collect_todos(ctx, files)
    ctx.state["tests"] = ctx.fns.summarize_tests(ctx)
    return ctx.fns.render_report(ctx, files, todos)
```

## Dogfood Evidence

This repo includes a real dogfood utility:
[`examples/repo_digest`](examples/repo_digest).

It is built with `proc-py` procedures:

```text
scan_files(ctx)
collect_todos(ctx)
summarize_tests(ctx)
render_report(ctx)
system_start(ctx)
```

Run it from the repo root:

```bash
PYTHONPATH=examples/repo_digest:. python3 examples/repo_digest/run_digest.py
```

Current output shape:

```text
# Repo Digest

- files scanned: 34
- Python files: 27
- TODO/FIXME/HACK matches: 0
- tests: 17 passed in 0.06s
- test duration: 0.351s

## Notable TODOs

- none
```

This repo also includes an agent workflow dogfood utility:
[`examples/agent_task_runtime`](examples/agent_task_runtime).

It models a coding-agent task loop with procedures:

```text
set_task(ctx, task)
inspect_repo(ctx)
find_relevant_files(ctx, task)
read_files(ctx, files)
run_checks(ctx)
summarize_checks(ctx, result)
build_llm_prompt(ctx)
ask_ollama(ctx, prompt)
render_pr_description(ctx)
system_start(ctx, task)
```

If local Ollama is available, it asks the configured model to draft the PR
description. The default dogfood model is `qwen2.5-coder:1.5b` for fast local
feedback. If Ollama is unavailable, times out, or the local runner fails, the
report falls back to deterministic text.

Run it from the repo root:

```bash
PYTHONPATH=examples/agent_task_runtime:. python3 examples/agent_task_runtime/run_agent_task.py \
  "add an agent task runtime dogfood example"
```

Dogfood verdict so far:

- writing small automation procedures feels natural;
- changing one file at a time is easy for an agent;
- `reload_fn` genuinely works because callers resolve dependencies through
  `ctx.fns`;
- app-local generated typing removes the worst `getattr(ctx.fns, "...")`
  friction;
- `ctx.config` remains a loose boundary and should be narrowed explicitly in
  procedures.

## Performance Snapshot

Measured on the current seed, mostly to catch obvious overhead mistakes:

```text
direct hello(ctx, "x"):              101 ns/op
ctx.fns.hello(ctx, "x"):             125 ns/op
getattr(ctx.fns, "hello")(ctx, "x"): 134 ns/op

create_ctx median:                   30.7 us
reload_fn("hello") median:           35.3 us
generate ctx_fns median:             96.5 us
1,000 ctx objects traced memory:      ~431 KiB

load_fns 100 funcs median:           640 us
reload_fns 100 funcs median:         5.1 ms
typegen 100 funcs median:            1.45 ms

local REPL eval HTTP median:         380 us
local REPL eval HTTP p95:            505 us
```

The runtime overhead is not the main risk. Disk, subprocesses, HTTP, DB, JSON,
and real business logic will dominate these costs. The main risk is whether the
architecture stays pleasant as examples become real tools.

## What Works

- Load one-function modules into `ctx.fns`.
- Reload one procedure with `reload_fn(ctx, "name")`.
- Reload all procedures with `reload_fns(ctx)`.
- Enforce one public callable defined per procedure module.
- Generate `Protocol` typing with real procedure signatures.
- Generate app-local `Fns` and `Ctx` Protocols for custom procedure packages.
- Use `ctx.state` and `ctx.t` for visible runtime/debug state.
- Run CLI commands: `list`, `call`, `new-fn`, `generate-types`, `repl`, `send`.
- Run a local REPL process with `load_all`, `reload`, and `eval`.
- Dogfood a small repo digest automation utility.
- Dogfood a small coding-agent task runtime utility.

## What This Is Not

This is not Django, FastAPI, Celery, Click, or a production app framework.

It does not provide:

- HTTP routing;
- database adapters;
- migrations;
- auth;
- background jobs;
- deployment;
- plugin discovery;
- a security model for remote eval.

It is a small experimental runtime and convention set. Grow adapters only after
a real use case demands them.

## Repository Layout

```text
proc_py/
  ctx.py          # Ctx, ctx.fns, config, state, scratch space
  loader.py       # load/reload procedure modules
  typegen.py      # generated Protocol typing for ctx.fns
  repl.py         # local dev REPL server/client helpers
  cli.py          # tiny command-line interface
  fns/            # seed procedures
examples/
  invoice_bot/    # tiny demo
  repo_digest/    # dogfood utility
  agent_task_runtime/ # coding-agent workflow dogfood utility
tests/
  test_runtime.py
```

## Roadmap

- Improve project/package options across CLI commands.
- Add better structured REPL errors.
- Add testing helpers for fake `Ctx` objects.
- Use the agent task runtime dogfood to test whether `ctx.state` needs typed
  state models.
- Keep this experimental unless repeated use cases prove it wants to become a
  mini-framework.

## License

MIT
