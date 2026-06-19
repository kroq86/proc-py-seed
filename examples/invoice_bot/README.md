# Invoice Bot Example

Tiny automation-style example for `proc-py`.

Run it from the repo root:

```bash
PYTHONPATH=examples/invoice_bot:. python3 examples/invoice_bot/run_demo.py
```

The example uses a custom procedure package:

```python
load_fns(ctx, "invoice_bot_fns")
```

This keeps the example separate from the seed package's own `proc_py.fns`.
