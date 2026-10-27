from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os


class Settings(BaseSettings):
    # === App ===
    APP_NAME: str = "HanziQuizz"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SQL_ECHO: bool = False

    # === Supabase Configuration ===
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_DB_PASSWORD: str = ""

    # === Database ===
    # Mặc định có thể điền PostgreSQL connection URI từ Supabase hoặc dùng SQLite
    DATABASE_URL: str = ""

    @property
    def effective_database_url(self) -> str:
        """
        Xác định URL kết nối database:
        1. Nếu DATABASE_URL được cung cấp trực tiếp (postgresql / sqlite).
        2. Nếu chỉ có SUPABASE_URL và SUPABASE_DB_PASSWORD thì tự động ghép thành PostgreSQL URI.
        3. Nếu không có thì fallback về SQLite cục bộ.
        """
        raw_url = (self.DATABASE_URL or "").strip()
        if raw_url:
            if raw_url.startswith("postgres://"):
                raw_url = raw_url.replace("postgres://", "postgresql://", 1)
            return raw_url

        if self.SUPABASE_URL and self.SUPABASE_DB_PASSWORD:
            import urllib.parse
            netloc = urllib.parse.urlparse(self.SUPABASE_URL).netloc
            if "." in netloc:
                project_ref = netloc.split(".")[0]
                encoded_pwd = urllib.parse.quote_plus(self.SUPABASE_DB_PASSWORD)
                # Kết nối trực tiếp qua db host của Supabase
                return f"postgresql://postgres:{encoded_pwd}@db.{project_ref}.supabase.co:5432/postgres"

        # Mặc định fallback SQLite
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
