from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LintResult:
    valid: bool
    errors: list[str]


class ChapterLinter:
    """Cheap deterministic checks performed before an LLM review."""

    def lint(self, draft: str) -> LintResult:
        errors: list[str] = []
        if not draft.strip():
            errors.append("Draft is empty")
        if "TODO" in draft or "<PLACEHOLDER>" in draft:
            errors.append("Draft contains placeholders")
        return LintResult(valid=not errors, errors=errors)
