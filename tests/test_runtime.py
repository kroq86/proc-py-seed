from __future__ import annotations

from importlib import invalidate_caches
from pathlib import Path
import shutil
import sys

from pytest import CaptureFixture, MonkeyPatch, raises

from proc_py import create_ctx, generate_ctx_fns_protocol, reload_fn, reload_fns
from proc_py.cli import main
from proc_py.ctx import Ctx
from proc_py.loader import load_fns
from proc_py.repl import handle_repl_request
from proc_py.scaffold import create_proc_file


def test_loads_functions_into_context() -> None:
    ctx = create_ctx()

    assert ctx.fns.hello(ctx, "python") == "hello, python"


def test_function_can_call_another_function_through_context() -> None:
    ctx = create_ctx({"prefix": "hi"})

    assert ctx.fns.system_start(ctx) == "hi, agent"


def test_context_has_runtime_state_and_repl_scratch_space() -> None:
    ctx = create_ctx()

    ctx.state["counter"] = 1
    ctx.t = {"last": "hello"}

    assert ctx.state == {"counter": 1}
    assert ctx.t == {"last": "hello"}


def test_reload_fn_replaces_function_and_preserves_context(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    package = _make_package(tmp_path, monkeypatch)
    _write_proc(package, "value", 'def value(ctx):\n    return ctx.config["answer"]\n')
    ctx = load_fns(Ctx(config={"answer": "old"}), "tmp_fns")

    _write_proc(package, "value", 'def value(ctx):\n    return ctx.config["answer"].upper()\n')
    reloaded = reload_fn(ctx, "value", "tmp_fns")

    assert reloaded is ctx
    assert ctx.config == {"answer": "old"}
    assert getattr(ctx.fns, "value")(ctx) == "OLD"


def test_reload_fns_reloads_all_functions_deterministically(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    package = _make_package(tmp_path, monkeypatch)
    _write_proc(package, "b_second", 'def b_second(ctx):\n    return "b1"\n')
    _write_proc(package, "a_first", 'def a_first(ctx):\n    return "a1"\n')
    ctx = load_fns(Ctx(), "tmp_fns")

    _write_proc(package, "a_first", 'def a_first(ctx):\n    return "a2"\n')
    _write_proc(package, "b_second", 'def b_second(ctx):\n    return "b2"\n')
    reloaded = reload_fns(ctx, "tmp_fns")

    assert reloaded is ctx
    assert getattr(ctx.fns, "a_first")(ctx) == "a2"
    assert getattr(ctx.fns, "b_second")(ctx) == "b2"


def test_reloaded_dependency_is_observed_through_context(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    package = _make_package(tmp_path, monkeypatch)
    _write_proc(package, "leaf", 'def leaf(ctx):\n    return "before"\n')
    _write_proc(package, "caller", "def caller(ctx):\n    return ctx.fns.leaf(ctx)\n")
    ctx = load_fns(Ctx(), "tmp_fns")

    _write_proc(package, "leaf", 'def leaf(ctx):\n    return "after"\n')
    reload_fn(ctx, "leaf", "tmp_fns")

    assert getattr(ctx.fns, "caller")(ctx) == "after"


def test_missing_function_export_raises_runtime_error(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    package = _make_package(tmp_path, monkeypatch)
    _write_proc(package, "missing", 'def other(ctx):\n    return "nope"\n')

    with raises(RuntimeError, match=r"tmp_fns\.missing must export callable missing\(\)"):
        load_fns(Ctx(), "tmp_fns")


def test_reload_fn_missing_module_raises_runtime_error(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    _make_package(tmp_path, monkeypatch)

    with raises(RuntimeError, match=r"procedure module tmp_fns\.missing could not be imported"):
        reload_fn(Ctx(), "missing", "tmp_fns")


def test_non_callable_matching_export_raises_runtime_error(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    package = _make_package(tmp_path, monkeypatch)
    _write_proc(package, "not_callable", "not_callable = 42\n")

    with raises(RuntimeError, match=r"tmp_fns\.not_callable\.not_callable must be callable"):
        load_fns(Ctx(), "tmp_fns")


def test_extra_public_callable_defined_in_module_raises_runtime_error(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    package = _make_package(tmp_path, monkeypatch)
    _write_proc(
        package,
        "one",
        'def one(ctx):\n    return "ok"\n\n\ndef extra(ctx):\n    return "nope"\n',
    )

    with raises(RuntimeError, match=r"tmp_fns\.one must define only public callable one\(\)"):
        load_fns(Ctx(), "tmp_fns")


def test_imported_public_callable_does_not_count_as_extra(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    package = _make_package(tmp_path, monkeypatch)
    _write_proc(
        package,
        "one",
        'from proc_py.ctx import Ctx\n\n\ndef one(ctx: Ctx):\n    return "ok"\n',
    )

    ctx = load_fns(Ctx(), "tmp_fns")

    assert getattr(ctx.fns, "one")(ctx) == "ok"


def test_generate_ctx_fns_protocol_writes_current_names(tmp_path: Path) -> None:
    output = generate_ctx_fns_protocol(output_path=tmp_path / "ctx_fns.py")

    content = output.read_text()
    assert "def hello(self, ctx: Ctx, name: str = 'world') -> str: ..." in content
    assert "def system_start(self, ctx: Ctx) -> str: ..." in content


def test_generate_ctx_fns_protocol_can_write_app_specific_context_type(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    package = _make_package(tmp_path, monkeypatch)
    _write_proc(package, "task", "def task(ctx, name: str) -> str:\n    return name\n")

    output = generate_ctx_fns_protocol(
        package="tmp_fns",
        output_path=tmp_path / "_ctx_types.py",
        protocol_name="TmpFns",
        ctx_protocol_name="TmpCtx",
    )

    content = output.read_text()
    assert "class TmpFns(Protocol):" in content
    assert "def task(self, ctx: TmpCtx, name: str) -> str: ..." in content
    assert "class TmpCtx(Protocol):" in content
    assert "fns: TmpFns" in content


def test_generate_ctx_fns_protocol_imports_app_local_state_types(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    package = _make_package(tmp_path, monkeypatch)
    (package / "_state.py").write_text(
        "from typing import TypedDict\n\n\nclass Result(TypedDict):\n    value: str\n"
    )
    _write_proc(
        package,
        "task",
        "from tmp_fns._state import Result\n\n\ndef task(ctx) -> Result:\n"
        "    return {'value': 'ok'}\n",
    )

    output = generate_ctx_fns_protocol(
        package="tmp_fns",
        output_path=tmp_path / "_ctx_types.py",
        protocol_name="TmpFns",
        ctx_protocol_name="TmpCtx",
    )

    content = output.read_text()
    assert "from tmp_fns._state import Result" in content
    assert "def task(self, ctx: TmpCtx) -> Result: ..." in content


def test_cli_lists_and_calls_procedures(capsys: CaptureFixture[str]) -> None:
    assert main(["list"]) == 0
    list_output = capsys.readouterr().out
    assert "hello" in list_output
    assert "system_start" in list_output

    assert main(["call", "hello", "python"]) == 0
    assert capsys.readouterr().out.strip() == "hello, python"


def test_create_proc_file_writes_one_function_module(tmp_path: Path) -> None:
    path = create_proc_file("draft_task", tmp_path)

    assert path == tmp_path / "draft_task.py"
    assert "def draft_task(ctx: Ctx) -> str:" in path.read_text()


def test_cli_new_fn_can_create_procedure_without_touching_real_package(
    tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    fns_dir = tmp_path / "fns"
    fns_dir.mkdir()

    assert main(["new-fn", "draft_cli", "--fns-dir", str(fns_dir), "--no-generate-types"]) == 0

    assert (fns_dir / "draft_cli.py").exists()
    assert "draft_cli.py" in capsys.readouterr().out


def test_repl_handler_load_reload_and_eval() -> None:
    ctx = create_ctx()
    session: dict[str, object] = {}

    loaded = handle_repl_request(ctx, session, {"op": "load_all"})
    evaluated = handle_repl_request(ctx, session, {"op": "eval", "code": 'hello(ctx, "repl")'})
    reloaded = handle_repl_request(ctx, session, {"op": "reload", "name": "hello"})

    assert loaded["count"] == 2
    assert evaluated == {"result": "hello, repl"}
    assert reloaded == {"ok": True, "name": "hello"}


def _make_package(tmp_path: Path, monkeypatch: MonkeyPatch) -> Path:
    monkeypatch.setattr(sys, "path", [str(tmp_path), *sys.path])
    for name in tuple(sys.modules):
        if name == "tmp_fns" or name.startswith("tmp_fns."):
            del sys.modules[name]
    package = tmp_path / "tmp_fns"
    package.mkdir()
    (package / "__init__.py").write_text('"""temporary procedure package."""\n')
    invalidate_caches()
    return package


def _write_proc(package: Path, name: str, source: str) -> None:
    (package / f"{name}.py").write_text(source)
    shutil.rmtree(package / "__pycache__", ignore_errors=True)
    invalidate_caches()
