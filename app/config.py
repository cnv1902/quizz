from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os


class Settings(BaseSettings):
    # === App ===
    APP_NAME: str = "HanziQuizz"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SQL_ECHO: bool = False

    # === Database ===
    # Kết nối trực tiếp PostgreSQL nội bộ Docker hoặc qua biến DATABASE_URL
    DATABASE_URL: str = "postgresql://postgres:quizz_secure_password_2024@localhost:5432/hanziquizz"

    @property
    def effective_database_url(self) -> str:
        """
        Xác định URL kết nối database:
        - Chuẩn hóa postgres:// thành postgresql:// cho SQLAlchemy.
        - Nếu rỗng thì fallback về SQLite.
        """
        raw_url = (self.DATABASE_URL or "").strip()
        if raw_url:
            if raw_url.startswith("postgres://"):
                raw_url = raw_url.replace("postgres://", "postgresql://", 1)
            return raw_url

        return "sqlite:///./hanziquizz.db"

    # === JWT Authentication ===
    SECRET_KEY: str = "hanziquizz-super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7

    # === Google OAuth2 ===
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback"
    GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL: str = "https://www.googleapis.com/oauth2/v3/userinfo"

    # === CORS ===
    FRONTEND_ORIGIN: str = "http://localhost:8000"

    # Cấu hình nạp biến môi trường từ .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
