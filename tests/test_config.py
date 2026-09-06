import pytest
from pydantic import ValidationError

from book_loop.infrastructure.config import Settings


def test_auth_security_settings_are_configurable():
    settings = Settings(
        auth_secret_key="long-random-secret-with-at-least-32-characters",
        auth_cookie_secure=True,
        auth_cookie_samesite="strict",
        cors_allowed_origins=["https://app.example.com"],
    )
    assert settings.auth_secret_key == "long-random-secret-with-at-least-32-characters"
    assert settings.auth_cookie_secure is True
    assert settings.auth_cookie_samesite == "strict"
    assert settings.cors_allowed_origins == ["https://app.example.com"]


def test_secure_cookie_configuration_rejects_short_secret():
    with pytest.raises(ValidationError, match="AUTH_SECRET_KEY"):
        Settings(auth_secret_key="too-short", auth_cookie_secure=True)


def test_cookie_samesite_configuration_rejects_unknown_value():
    with pytest.raises(ValidationError, match="AUTH_COOKIE_SAMESITE"):
        Settings(auth_cookie_samesite="invalid")
