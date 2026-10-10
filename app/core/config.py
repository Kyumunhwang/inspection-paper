"""Application configuration settings."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Configuration settings loaded from environment variables."""

    APP_NAME: str = "Inspection paper"
    APP_ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 3088

    # Google OAuth 2.0 Credentials
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "https://inspection-paper-923588298450.asia-northeast3.run.app/api/auth/google/callback"
    GOOGLE_SCOPES: list[str] = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    # Google Drive & Gemini
    DEFAULT_FOLDER_ID: str = "1A2b3C4d_LIS2025_ExamMid"
    GEMINI_API_KEY: str = ""

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
