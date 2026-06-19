from __future__ import annotations

from importlib import import_module
from inspect import signature
from pathlib import Path
from re import sub
from typing import Callable, cast

from proc_py.loader import iter_proc_names


def generate_ctx_fns_protocol(
    package: str = "proc_py.fns",
    output_path: str | Path = "proc_py/ctx_fns.py",
    protocol_name: str = "CtxFns",
    ctx_protocol_name: str | None = None,
) -> Path:
    """Generate the CtxFns protocol for loaded procedure names."""

    names = iter_proc_names(package)
    modules = [import_module(f"{package}.{name}") for name in names]
    fns = [
        cast(Callable[..., object], getattr(module, name))
        for module, name in zip(modules, names, strict=True)
    ]
    app_local_types = _app_local_annotation_names(package, fns) if ctx_protocol_name else []
    output = Path(output_path)
    typing_imports = "Any, Protocol" if ctx_protocol_name else "TYPE_CHECKING, Protocol"
    lines = [
        "from __future__ import annotations",
        "",
        f"from typing import {typing_imports}",
        "",
    ]
    if app_local_types:
        lines.extend(
            [
                f"from {package}._state import {', '.join(app_local_types)}",
                "",
            ]
        )
    if not ctx_protocol_name:
        lines.extend(
            [
                "if TYPE_CHECKING:",
                "    from proc_py.ctx import Ctx",
                "",
                "",
            ]
        )
    lines.extend(
        [
            f"class {protocol_name}(Protocol):",
            '    """Generated registry protocol for procedures loaded into ctx.fns."""',
            "",
        ]
    )
    if names:
        for name, fn in zip(names, fns, strict=True):
            fn_signature = _signature_for_protocol(fn, ctx_protocol_name)
            for type_name in app_local_types:
                fn_signature = fn_signature.replace(f"{package}._state.{type_name}", type_name)
            lines.append(
                f"    def {name}{fn_signature}: ..."
            )
    else:
        lines.append("    pass")

    if ctx_protocol_name:
        lines.extend(
            [
                "",
                "",
                f"class {ctx_protocol_name}(Protocol):",
                '    """Generated context protocol with app-specific ctx.fns typing."""',
                "",
                f"    fns: {protocol_name}",
                "    config: dict[str, Any]",
                "    state: dict[str, Any]",
                "    t: Any",
            ]
        )

    output.write_text("\n".join(lines) + "\n")
    return output


def _app_local_annotation_names(package: str, fns: list[Callable[..., object]]) -> list[str]:
    try:
        state_module = import_module(f"{package}._state")
    except ModuleNotFoundError:
        return []

    state_names = {
        name
        for name, value in vars(state_module).items()
        if not name.startswith("_")
        and isinstance(value, type)
        and getattr(value, "__module__", None) == state_module.__name__
    }
    used: set[str] = set()
    for fn in fns:
        for annotation in getattr(fn, "__annotations__", {}).values():
            text = annotation if isinstance(annotation, str) else getattr(annotation, "__name__", "")
            for name in state_names:
                if name in text:
                    used.add(name)
    return sorted(used)


def _signature_for_protocol(
    fn: Callable[..., object], ctx_protocol_name: str | None = None
) -> str:
    fn_signature = str(signature(fn)).replace("'Ctx'", "Ctx")
    fn_signature = sub(r": '([A-Za-z_][A-Za-z0-9_\.\[\], ]*)'", r": \1", fn_signature)
    fn_signature = sub(r" -> '([A-Za-z_][A-Za-z0-9_\.\[\], ]*)'", r" -> \1", fn_signature)
    if ctx_protocol_name:
        fn_signature = sub(r"\((ctx: )Ctx([,)])", rf"(\1{ctx_protocol_name}\2", fn_signature)
        fn_signature = sub(r"\(ctx([,)])", rf"(ctx: {ctx_protocol_name}\1", fn_signature)
    if fn_signature == "()":
        return "(self)"
    return f"(self, {fn_signature[1:]}"
