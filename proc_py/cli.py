from __future__ import annotations

from argparse import ArgumentParser, Namespace
from json import dumps
from typing import Any, Sequence

from proc_py.loader import iter_proc_names, reload_fn
from proc_py.repl import send_repl_request, serve_repl
from proc_py.runtime import create_ctx
from proc_py.scaffold import create_proc_file
from proc_py.typegen import generate_ctx_fns_protocol


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = args.func(args)
    if result is not None:
        print(_format_result(result))
    return 0


def _build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="proc-py")
    subcommands = parser.add_subparsers(required=True)

    list_parser = subcommands.add_parser("list", help="list available procedure names")
    list_parser.set_defaults(func=_cmd_list)

    call_parser = subcommands.add_parser("call", help="call a local procedure")
    call_parser.add_argument("name")
    call_parser.add_argument("args", nargs="*")
    call_parser.set_defaults(func=_cmd_call)

    reload_parser = subcommands.add_parser("reload", help="reload a local procedure once")
    reload_parser.add_argument("name")
    reload_parser.set_defaults(func=_cmd_reload)

    typegen_parser = subcommands.add_parser("generate-types", help="generate ctx.fns protocol")
    typegen_parser.add_argument("--package", default="proc_py.fns")
    typegen_parser.add_argument("--output", default="proc_py/ctx_fns.py")
    typegen_parser.add_argument("--protocol-name", default="CtxFns")
    typegen_parser.add_argument("--ctx-protocol-name")
    typegen_parser.set_defaults(func=_cmd_generate_types)

    new_fn_parser = subcommands.add_parser("new-fn", help="create a new procedure file")
    new_fn_parser.add_argument("name")
    new_fn_parser.add_argument("--fns-dir", default="proc_py/fns")
    new_fn_parser.add_argument("--types-out", default="proc_py/ctx_fns.py")
    new_fn_parser.add_argument("--no-generate-types", action="store_true")
    new_fn_parser.set_defaults(func=_cmd_new_fn)

    repl_parser = subcommands.add_parser("repl", help="start a local REPL server")
    repl_parser.add_argument("--host", default="127.0.0.1")
    repl_parser.add_argument("--port", type=int, default=3001)
    repl_parser.set_defaults(func=_cmd_repl)

    send_parser = subcommands.add_parser("send", help="send a command to a REPL server")
    send_parser.add_argument("--host", default="127.0.0.1")
    send_parser.add_argument("--port", type=int, default=3001)
    send_subcommands = send_parser.add_subparsers(dest="send_op", required=True)

    send_load = send_subcommands.add_parser("load_all", help="reload all procedures in REPL")
    send_load.set_defaults(func=_cmd_send)

    send_reload = send_subcommands.add_parser("reload", help="reload one procedure in REPL")
    send_reload.add_argument("name")
    send_reload.set_defaults(func=_cmd_send)

    send_eval = send_subcommands.add_parser("eval", help="evaluate Python code in REPL")
    send_eval.add_argument("code")
    send_eval.set_defaults(func=_cmd_send)

    return parser


def _cmd_list(args: Namespace) -> list[str]:
    return iter_proc_names()


def _cmd_call(args: Namespace) -> Any:
    ctx = create_ctx()
    fn = getattr(ctx.fns, args.name)
    return fn(ctx, *args.args)


def _cmd_reload(args: Namespace) -> dict[str, str | bool]:
    ctx = create_ctx()
    reload_fn(ctx, args.name)
    return {"ok": True, "name": args.name}


def _cmd_generate_types(args: Namespace) -> str:
    return str(
        generate_ctx_fns_protocol(
            package=args.package,
            output_path=args.output,
            protocol_name=args.protocol_name,
            ctx_protocol_name=args.ctx_protocol_name,
        )
    )


def _cmd_new_fn(args: Namespace) -> dict[str, str]:
    path = create_proc_file(args.name, args.fns_dir)
    result = {"created": str(path)}
    if not args.no_generate_types:
        type_path = generate_ctx_fns_protocol(output_path=args.types_out)
        result["types"] = str(type_path)
    return result


def _cmd_repl(args: Namespace) -> None:
    serve_repl(args.host, args.port)


def _cmd_send(args: Namespace) -> dict[str, Any]:
    request: dict[str, Any]
    if args.send_op == "load_all":
        request = {"op": "load_all"}
    elif args.send_op == "reload":
        request = {"op": "reload", "name": args.name}
    elif args.send_op == "eval":
        request = {"op": "eval", "code": args.code}
    else:
        raise RuntimeError(f"unknown send op: {args.send_op}")
    return send_repl_request(request, args.host, args.port)


def _format_result(result: Any) -> str:
    if isinstance(result, str):
        return result
    return dumps(result, indent=2, sort_keys=True, default=repr)


if __name__ == "__main__":
    raise SystemExit(main())
