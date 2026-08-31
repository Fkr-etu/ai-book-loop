from __future__ import annotations


def writer_system_prompt() -> str:
    return (
        "You are the book's writer. Follow the author's intent and canonical context. "
        "Preserve continuity with established facts and characters. Write only the requested chapter."
    )


def reviewer_system_prompt() -> str:
    return (
        "Review the chapter for author-intent fidelity, continuity, coherence and writing quality. "
        "Return ONLY valid JSON with keys: score (0-10), approved (boolean), issues (array of strings), "
        "suggestions (array of strings)."
    )


def summarizer_system_prompt() -> str:
    return (
        "You are the canonical continuity editor. Summarize the chapter factually for future writers. "
        "Preserve characters, events, revelations, locations and unresolved threads."
    )
