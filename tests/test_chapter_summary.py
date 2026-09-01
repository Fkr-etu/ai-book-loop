from book_loop.domain.value_objects import ChapterSummary


def test_chapter_summary_keeps_identity_and_text() -> None:
    summary = ChapterSummary(
        chapter_number=3,
        title="The Revelation",
        summary="Alice discovers the truth about Bob.",
    )

    assert summary.chapter_number == 3
    assert summary.title == "The Revelation"
    assert summary.summary == "Alice discovers the truth about Bob."
    assert summary.render() == "Chapter 3 (The Revelation): Alice discovers the truth about Bob."
