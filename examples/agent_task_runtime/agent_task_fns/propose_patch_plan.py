from __future__ import annotations

from typing import cast

from agent_task_fns._ctx_types import AgentTaskCtx


def propose_patch_plan(ctx: AgentTaskCtx) -> str:
    task = str(ctx.state.get("task", ""))
    check_summary = str(ctx.state.get("check_summary", "not run"))
    files = _string_list(ctx.state.get("relevant_files", []))
    file_text = cast(object, ctx.state.get("file_text", {}))
    snippets: list[str] = []
    if isinstance(file_text, dict):
        text_by_file = cast(dict[object, object], file_text)
        for file_name in files[:3]:
            text = text_by_file.get(file_name, "")
            if isinstance(text, str):
                snippets.append(f"### {file_name}\n{text[:700]}")

    plan = _fallback_plan(task, files, check_summary)
    prompt = "\n\n".join(
        [
            "You are reviewing a deterministic patch plan. Do not write a patch.",
            "Do not invent dependencies; this repo intentionally uses the Python standard library.",
            "Do not propose creating files or functions that already exist.",
            "Return short Markdown notes with sections: Useful, Risks, Missing Context.",
            "Keep it under 120 words.",
            "",
            "Deterministic patch plan:",
            plan,
            "Use only the provided task, checks, file list, and snippets.",
            "",
            f"Task: {task}",
            f"Checks: {check_summary}",
            "Relevant files:\n" + "\n".join(f"- {file_name}" for file_name in files),
            "Snippets:\n" + "\n\n".join(snippets),
        ]
    )
    notes = ctx.fns.ask_ollama(ctx, prompt)
    if notes:
        ctx.state["llm_patch_notes"] = notes
    ctx.state["patch_plan"] = plan
    return plan


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in cast(list[object], value):
        if isinstance(item, str):
            result.append(item)
    return result


def _fallback_plan(task: str, files: list[str], check_summary: str) -> str:
    lines = [
        "### Goal",
        task or "Inspect the task and repository context.",
        "",
        "### Files to edit",
    ]
    if files:
        lines.extend(f"- `{file_name}`" for file_name in files[:8])
    else:
        lines.append("- No relevant files were identified.")
    lines.extend(
        [
            "",
            "### Implementation steps",
            "- Review the relevant files.",
            "- Make the smallest change that satisfies the task.",
            "- Keep procedure boundaries small and explicit.",
            "",
            "### Tests to run",
            f"- Current check summary: {check_summary}",
        ]
    )
    return "\n".join(lines)
