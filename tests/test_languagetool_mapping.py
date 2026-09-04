from book_loop.domain.models import DiagnosticCategory
from book_loop.infrastructure.linguistic.languagetool import LanguageToolChecker


def diagnostic(category_id: str, issue_type: str = "grammar") -> DiagnosticCategory:
    return LanguageToolChecker._diagnostic(
        {
            "offset": 0,
            "length": 4,
            "message": "test",
            "rule": {"id": "TEST", "issueType": issue_type, "categoryId": category_id},
            "replacements": [],
        },
        "Test",
        language="fr",
    ).category


def test_maps_specific_language_tool_categories() -> None:
    assert diagnostic("TYPOS") == DiagnosticCategory.SPELLING
    assert diagnostic("AGREEMENT") == DiagnosticCategory.AGREEMENT
    assert diagnostic("CONJUGATION") == DiagnosticCategory.CONJUGATION
    assert diagnostic("PUNCTUATION") == DiagnosticCategory.PUNCTUATION
    assert diagnostic("TYPOGRAPHY") == DiagnosticCategory.TYPOGRAPHY
    assert diagnostic("STYLE", "style") == DiagnosticCategory.STYLE


def test_unknown_category_keeps_issue_type_fallback() -> None:
    assert diagnostic("UNKNOWN", "misspelling") == DiagnosticCategory.SPELLING
