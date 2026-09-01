from book_loop.application.services.linter import ChapterLinter


def test_empty_draft_is_invalid() -> None:
    result = ChapterLinter().lint("   ")
    assert not result.valid
    assert "Draft is empty" in result.errors


def test_placeholder_is_invalid() -> None:
    result = ChapterLinter().lint("A scene TODO")
    assert not result.valid


def test_normal_draft_is_valid() -> None:
    result = ChapterLinter().lint("A complete scene.")
    assert result.valid
