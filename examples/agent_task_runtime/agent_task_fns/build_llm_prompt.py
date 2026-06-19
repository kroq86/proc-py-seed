from __future__ import annotations

from typing import cast

from agent_task_fns._ctx_types import AgentTaskCtx


def build_llm_prompt(ctx: AgentTaskCtx) -> str:
    task = str(ctx.state.get("task", ""))
    check_summary = str(ctx.state.get("check_summary", "not run"))
    file_text = cast(object, ctx.state.get("file_text", {}))
    relevant = cast(object, ctx.state.get("relevant_files", []))
    files: list[str] = []
    if isinstance(relevant, list):
        for item in cast(list[object], relevant):
            if isinstance(item, str):
                files.append(item)

    snippets: list[str] = []
    if isinstance(file_text, dict):
        text_by_file = cast(dict[object, object], file_text)
        for file_name in files[:3]:
            text = text_by_file.get(file_name, "")
            if isinstance(text, str):
                snippets.append(f"### {file_name}\n{text[:600]}")

    return "\n\n".join(
        [
            "You are helping write a concise pull request description for a Python repo.",
            "Use only the task, file list, check summary, and snippets below.",
            "Return Markdown with sections: Summary, Key Files, Checks, Risks.",
            "",
            f"Task: {task}",
            f"Checks: {check_summary}",
            "Relevant files:\n" + "\n".join(f"- {file_name}" for file_name in files),
            "Snippets:\n" + "\n\n".join(snippets),
        ]
    )
