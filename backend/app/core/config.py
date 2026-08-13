"""
Central configuration for AURA.
All secrets are read from environment variables (.env). Never hardcode keys.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


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


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
