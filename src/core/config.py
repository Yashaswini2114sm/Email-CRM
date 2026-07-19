from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Email CRM API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/email_crm"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "change-this-to-a-random-secret-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenAI
    OPENAI_API_KEY: str = ""

    # Email
    MAIL_IMAP_SERVER: str = "imap.gmail.com"
    MAIL_IMAP_PORT: int = 993
    MAIL_SMTP_SERVER: str = "smtp.gmail.com"
    MAIL_SMTP_PORT: int = 587
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )


settings = Settings()
