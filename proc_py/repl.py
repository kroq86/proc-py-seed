from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import JSONDecodeError, dumps, loads
from typing import Any, cast
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from proc_py.ctx import Ctx
from proc_py.loader import iter_proc_names, load_fns, reload_fn
from proc_py.runtime import create_ctx


def serve_repl(host: str = "127.0.0.1", port: int = 3001) -> None:
    """Start a local development REPL server."""

    ctx = create_ctx()
    session: dict[str, Any] = {}

    class ReplHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            if self.path != "/repl":
                self._send_json({"error": "not found"}, status=404)
                return

            try:
                request = self._read_json()
                response = handle_repl_request(ctx, session, request)
                self._send_json(response)
            except Exception as exc:
                self._send_json({"error": str(exc), "type": type(exc).__name__}, status=500)

        def log_message(self, format: str, *args: object) -> None:
            return

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("content-length", "0"))
            try:
                body = self.rfile.read(length)
                data = loads(body.decode("utf-8"))
            except JSONDecodeError as exc:
                raise RuntimeError("request body must be JSON") from exc
            if not isinstance(data, dict):
                raise RuntimeError("request body must be a JSON object")
            return cast(dict[str, Any], data)

        def _send_json(self, data: dict[str, Any], status: int = 200) -> None:
            body = dumps(data, default=repr).encode("utf-8")
            self.send_response(status)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer((host, port), ReplHandler)
    print(f"repl server on http://{host}:{server.server_port}/repl", flush=True)
    server.serve_forever()


def handle_repl_request(
    ctx: Ctx, session: dict[str, Any], request: dict[str, Any]
) -> dict[str, Any]:
    op = request.get("op")
    if op == "load_all":
        load_fns(ctx)
        names = iter_proc_names()
        return {"loaded": names, "count": len(names)}
    if op == "reload":
        name = request.get("name")
        if not isinstance(name, str) or not name:
            raise RuntimeError("reload requires a non-empty name")
        reload_fn(ctx, name)
        return {"ok": True, "name": name}
    if op == "eval":
        code = request.get("code")
        if not isinstance(code, str) or not code:
            raise RuntimeError("eval requires non-empty code")
        return {"result": _eval_code(ctx, session, code)}
    raise RuntimeError(f"unknown op: {op}")


def send_repl_request(
    request: dict[str, Any], host: str = "127.0.0.1", port: int = 3001
) -> dict[str, Any]:
    body = dumps(request).encode("utf-8")
    http_request = Request(
        f"http://{host}:{port}/repl",
        data=body,
        headers={"content-type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(http_request, timeout=5) as response:
            data = loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        data = loads(exc.read().decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("repl server returned a non-object JSON response")
    return cast(dict[str, Any], data)


def _eval_code(ctx: Ctx, session: dict[str, Any], code: str) -> Any:
    env: dict[str, Any] = {
        "ctx": ctx,
        "session": session,
        **{name: getattr(ctx.fns, name) for name in iter_proc_names()},
    }
    try:
        return eval(code, {}, env)
    except SyntaxError:
        exec(code, {}, env)
        return env.get("_")
