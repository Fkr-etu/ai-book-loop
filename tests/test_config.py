from book_loop.infrastructure.config import Settings


def test_auth_security_settings_are_configurable():
    settings = Settings(
        auth_secret_key="long-random-secret",
        auth_cookie_secure=True,
        auth_cookie_samesite="strict",
        cors_allowed_origins=["https://app.example.com"],
    )
    assert settings.auth_secret_key == "long-random-secret"
    assert settings.auth_cookie_secure is True
    assert settings.auth_cookie_samesite == "strict"
    assert settings.cors_allowed_origins == ["https://app.example.com"]
