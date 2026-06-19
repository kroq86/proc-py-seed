from __future__ import annotations

from json import dumps, loads
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from agent_task_fns._ctx_types import AgentTaskCtx


def ask_ollama(ctx: AgentTaskCtx, prompt: str) -> str:
    host = str(ctx.config.get("ollama_host", "http://127.0.0.1:11434"))
    model = str(ctx.config.get("ollama_model", "qwen2.5-coder:7b"))
    timeout = float(ctx.config.get("ollama_timeout", 30))
    body = dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 220,
                "num_gpu": 0,
            },
        }
    ).encode("utf-8")
    request = Request(
        f"{host.rstrip('/')}/api/generate",
        data=body,
        headers={"content-type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            data = loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        ctx.state["ollama_error"] = f"HTTP {exc.code}: {body_text or exc.reason}"
        return ""
    except (URLError, TimeoutError) as exc:
        ctx.state["ollama_error"] = str(exc)
        return ""

    if not isinstance(data, dict):
        ctx.state["ollama_error"] = "Ollama returned non-object JSON"
        return ""
    result = cast(dict[str, Any], data)
    text = result.get("response", "")
    if not isinstance(text, str):
        ctx.state["ollama_error"] = "Ollama response field is not a string"
        return ""
    return text.strip()
