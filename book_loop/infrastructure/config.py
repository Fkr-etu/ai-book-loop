from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "gemini"
    llm_model: str = "gemini-3.6-flash"
    gemini_api_key: str = ""
    database_url: str = "sqlite:///./book_loop.db"
    max_retries: int = 3
    review_threshold: int = 7
    auth_secret_key: str = ""
    auth_cookie_secure: bool = False
    auth_cookie_samesite: str = "lax"
    cors_allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
