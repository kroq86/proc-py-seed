from __future__ import annotations

from typing import cast

from agent_task_fns._ctx_types import AgentTaskCtx
from agent_task_fns._state import file_text, relevant_files


def propose_patch_plan(ctx: AgentTaskCtx) -> str:
    task = str(ctx.state.get("task", ""))
    check_summary = str(ctx.state.get("check_summary", "not run"))
    detected_checks = _string_list(ctx.state.get("detected_checks", []))
    files = relevant_files(ctx)
    text_by_file = file_text(ctx)
    snippets: list[str] = []
    for file_name in files[:3]:
        text = text_by_file.get(file_name, "")
        if text:
            snippets.append(f"### {file_name}\n{text[:700]}")

    plan = _fallback_plan(task, files, check_summary, detected_checks)
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
            "Detected checks:\n" + "\n".join(f"- {check}" for check in detected_checks),
            "Relevant files:\n" + "\n".join(f"- {file_name}" for file_name in files),
            "Snippets:\n" + "\n\n".join(snippets),
        ]
    )
    notes = ctx.fns.ask_ollama(ctx, prompt)
    if notes:
        ctx.state["llm_patch_notes"] = notes
    ctx.state["patch_plan"] = plan
    return plan


def _fallback_plan(
    task: str, files: list[str], check_summary: str, detected_checks: list[str]
) -> str:
    task_lower = task.lower()
    implementation_steps = [
        "- Review the relevant files.",
        "- Make the smallest change that satisfies the task.",
        "- Keep procedure boundaries small and explicit.",
    ]
    if any(word in task_lower for word in ("type", "typing", "protocol", "ctx.fns")):
        implementation_steps.append("- Regenerate app-local ctx.fns Protocols after signature changes.")
    if any(word in task_lower for word in ("ollama", "llm", "prompt")):
        implementation_steps.append("- Keep local LLM usage optional and preserve deterministic fallback behavior.")
    if any(word in task_lower for word in ("test", "check", "pyright")):
        implementation_steps.append("- Keep verification commands explicit in the report.")

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
            *implementation_steps,
            "",
            "### Tests to run",
            f"- Current check summary: {check_summary}",
            *[f"- `{check}`" for check in detected_checks],
            "- Agent dogfood workflow for this task",
        ]
    )
    return "\n".join(lines)


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in cast(list[object], value):
        if isinstance(item, str):
            result.append(item)
    return result
