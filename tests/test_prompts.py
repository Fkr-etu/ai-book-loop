from book_loop.application.services.prompts import (
    writer_system_prompt,
    reviewer_system_prompt,
    summarizer_system_prompt,
)


def test_prompts_templates_exist():
    assert "writer" in writer_system_prompt().lower()
    assert "review" in reviewer_system_prompt().lower()
    assert "continuity" in summarizer_system_prompt().lower()
