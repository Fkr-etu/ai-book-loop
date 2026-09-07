from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "gemini"
    llm_model: str = "gemini-3.6-flash"
    gemini_api_key: str = ""
    database_url: str = "postgresql://book_loop:book_loop@localhost:5432/book_loop"
    max_retries: int = 3
    review_threshold: int = 7
    linguistic_checker: str = "disabled"
    language_tool_url: str = "http://localhost:8010"
    linguistic_language: str = "fr"
    spacy_model: str = "fr_core_news_sm"
    auth_secret_key: str = ""
    auth_cookie_secure: bool = False
    auth_cookie_samesite: str = "lax"
    auth_login_rate_limit: int = 5
    auth_login_rate_window_seconds: int = 900
    auth_login_ip_rate_limit: int = 5
    auth_login_ip_rate_window_seconds: int = 900
    auth_register_rate_limit: int = 10
    auth_register_rate_window_seconds: int = 900
    cors_allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_creator_monthly_price_id: str = ""
    stripe_creator_yearly_price_id: str = ""
    stripe_pro_monthly_price_id: str = ""
    stripe_pro_yearly_price_id: str = ""
    stripe_success_url: str = "http://localhost:3000/billing/success"
    stripe_cancel_url: str = "http://localhost:3000/pricing"
    stripe_portal_return_url: str = "http://localhost:3000/studio"

    @model_validator(mode="after")
    def validate_auth_security(self) -> "Settings":
        if self.auth_cookie_samesite not in {"lax", "strict", "none"}:
            raise ValueError("AUTH_COOKIE_SAMESITE must be lax, strict, or none")
        if self.auth_cookie_secure and len(self.auth_secret_key) < 32:
            raise ValueError("AUTH_SECRET_KEY must contain at least 32 characters when secure cookies are enabled")
        return self
