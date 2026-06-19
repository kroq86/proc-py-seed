from __future__ import annotations

from importlib import import_module, reload
from pathlib import Path
from types import ModuleType
from typing import Callable

from proc_py.ctx import Ctx, ProcFn


def load_fns(ctx: Ctx, package: str = "proc_py.fns") -> Ctx:
    """Load one-function modules from a package into ctx.fns."""

    for file_path in _iter_proc_files(package):
        fn_name = file_path.stem
        module = import_module(f"{package}.{fn_name}")
        ctx.register(fn_name, _proc_fn_from_module(module, fn_name))

    return ctx


def reload_fn(ctx: Ctx, name: str, package: str = "proc_py.fns") -> Ctx:
    """Reload one procedure module and replace its function in ctx.fns."""

    try:
        module = import_module(f"{package}.{name}")
    except ModuleNotFoundError as exc:
        if exc.name == f"{package}.{name}":
            raise RuntimeError(f"procedure module {package}.{name} could not be imported") from exc
        raise

    module = reload(module)
    ctx.register(name, _proc_fn_from_module(module, name))
    return ctx


def reload_fns(ctx: Ctx, package: str = "proc_py.fns") -> Ctx:
    """Reload all one-function modules from a package into ctx.fns."""

    for file_path in _iter_proc_files(package):
        reload_fn(ctx, file_path.stem, package)

    return ctx


def iter_proc_names(package: str = "proc_py.fns") -> list[str]:
    """Return procedure names available in a package in deterministic order."""

    return [file_path.stem for file_path in _iter_proc_files(package)]


def _iter_proc_files(package: str) -> list[Path]:
    package_module = import_module(package)
    package_path = _module_path(package_module)

    return sorted(
        file_path
        for file_path in package_path.glob("*.py")
        if not file_path.name.startswith("_")
    )


def _module_path(module: ModuleType) -> Path:
    if module.__file__ is None:
        raise RuntimeError(f"package {module.__name__} has no filesystem path")
    return Path(module.__file__).parent


def _proc_fn_from_module(module: ModuleType, name: str) -> ProcFn:
    fn = getattr(module, name, None)
    if fn is None:
        raise RuntimeError(f"{module.__name__} must export callable {name}()")
    if not callable(fn):
        raise RuntimeError(f"{module.__name__}.{name} must be callable")
    extra_names = [
        public_name
        for public_name, value in vars(module).items()
        if public_name != name
        and not public_name.startswith("_")
        and callable(value)
        and getattr(value, "__module__", None) == module.__name__
    ]
    if extra_names:
        extras = ", ".join(sorted(extra_names))
        raise RuntimeError(
            f"{module.__name__} must define only public callable {name}(); found {extras}"
        )
    return _as_proc_fn(fn)


def _as_proc_fn(fn: Callable[..., object]) -> ProcFn:
    return fn
