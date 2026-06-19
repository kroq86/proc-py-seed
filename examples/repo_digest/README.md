# Repo Digest Dogfood

Small dogfood utility built with `proc-py`.

Run from the repo root:

```bash
PYTHONPATH=examples/repo_digest:. python3 examples/repo_digest/run_digest.py
```

It scans the repository, collects TODO-style comments, runs the test command,
and renders a markdown digest.

Regenerate app-local typing after changing procedure names or signatures:

```bash
PYTHONPATH=examples/repo_digest:. python3 -m proc_py.cli generate-types \
  --package repo_digest_fns \
  --output examples/repo_digest/repo_digest_fns/_ctx_types.py \
  --protocol-name RepoDigestFns \
  --ctx-protocol-name RepoDigestCtx
```

The generated `_ctx_types.py` file lets dogfood procedures call
`ctx.fns.scan_files(ctx)` directly while keeping Pyright aware of custom
procedure names.
