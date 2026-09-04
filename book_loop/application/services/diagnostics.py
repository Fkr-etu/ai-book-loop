from __future__ import annotations

from collections.abc import Iterable

from book_loop.domain.models import Diagnostic, DiagnosticSeverity, DiagnosticSource


_SEVERITY_RANK = {
    DiagnosticSeverity.SUGGESTION: 0,
    DiagnosticSeverity.WARNING: 1,
    DiagnosticSeverity.ERROR: 2,
}


def _key(diagnostic: Diagnostic) -> tuple[object, ...]:
    return (
        diagnostic.category,
        diagnostic.start_offset,
        diagnostic.end_offset,
        diagnostic.original_text,
        diagnostic.message.casefold().strip(),
    )


def fuse_diagnostics(diagnostics: Iterable[Diagnostic]) -> list[Diagnostic]:
    """Merge duplicate findings while preserving provider provenance."""
    merged: dict[tuple[object, ...], Diagnostic] = {}
    sources: dict[tuple[object, ...], set[DiagnosticSource]] = {}

    for diagnostic in diagnostics:
        key = _key(diagnostic)
        existing = merged.get(key)
        sources.setdefault(key, set()).add(diagnostic.source)
        if existing is None:
            merged[key] = diagnostic.model_copy(deep=True)
            continue
        if _SEVERITY_RANK[diagnostic.severity] > _SEVERITY_RANK[existing.severity]:
            existing.severity = diagnostic.severity
        existing.confidence = max(existing.confidence, diagnostic.confidence)
        existing.suggestions = list(dict.fromkeys(existing.suggestions + diagnostic.suggestions))
        if not existing.rule_id:
            existing.rule_id = diagnostic.rule_id
        if not existing.related_assertion_id:
            existing.related_assertion_id = diagnostic.related_assertion_id
        existing.metadata.update(diagnostic.metadata)

    result = []
    for key, diagnostic in merged.items():
        provider_sources = sorted(sources[key], key=lambda source: source.value)
        diagnostic.metadata["sources"] = ",".join(source.value for source in provider_sources)
        if len(provider_sources) > 1:
            diagnostic.source = DiagnosticSource.FUSION
        result.append(diagnostic)

    return sorted(
        result,
        key=lambda item: (
            item.start_offset is None,
            item.start_offset if item.start_offset is not None else 0,
            -_SEVERITY_RANK[item.severity],
            item.category.value,
            item.message.casefold(),
        ),
    )
