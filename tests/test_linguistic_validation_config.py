from book_loop.infrastructure.config import Settings


def test_linguistic_checker_defaults_to_safe_disabled_mode():
    settings = Settings(_env_file=None)

    assert settings.linguistic_checker == "disabled"
    assert settings.language_tool_url == "http://localhost:8010"
    assert settings.linguistic_language == "fr"
