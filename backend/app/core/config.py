"""
Central configuration for AURA.
All secrets are read from environment variables (.env). Never hardcode keys.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_origin(value: str, default_scheme: str = "https") -> str:
    """Turn a hostname such as service.onrender.com into a valid origin URL."""
    value = (value or "").strip().rstrip("/")
    if not value:
        return value
    if value.startswith(("http://", "https://")):
        return value
    if value.startswith(("localhost", "127.0.0.1")):
        return f"http://{value}"
    return f"{default_scheme}://{value}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    APP_NAME: str = "AURA"
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    # --- Security ---
    SECRET_KEY: str = "change-this-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./aura.db"

    # --- Gemini ---
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # --- Google OAuth ---
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    # --- Sync ---
    AUTO_SYNC_INTERVAL_MINUTES: int = 15
    MAX_EMAILS_PER_SYNC: int = 40

    @property
    def frontend_origin(self) -> str:
        return normalize_origin(self.FRONTEND_URL)

    @property
    def backend_origin(self) -> str:
        return normalize_origin(self.BACKEND_URL)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
