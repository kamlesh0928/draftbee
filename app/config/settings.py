from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    # Database
    DATABASE_URL: str

    # Discord
    DISCORD_BOT_TOKEN: str
    DISCORD_SERVER_ID: int
    DISCORD_APPROVAL_CHANNEL_ID: int

    # Gemini
    GEMINI_API_KEY: str
    GEMINI_MODEL: str

    # LinkedIn
    LINKEDIN_CLIENT_ID: str
    LINKEDIN_CLIENT_SECRET: str
    LINKEDIN_ACCESS_TOKEN: str
    LINKEDIN_REFRESH_TOKEN: str
    LINKEDIN_PERSON_ID: str
    LINKEDIN_API_VERSION: str

    # X
    X_BEARER_TOKEN: str
    X_API_KEY: str
    X_API_SECRET: str
    X_CLIENT_ID: str
    X_CLIENT_SECRET: str
    X_ACCESS_TOKEN: str
    X_ACCESS_TOKEN_SECRET: str


settings = Settings()

TOPICS = [
    "Data Structures and Algorithms",
    "System Design",
    "Full Stack Development",
    "Machine Learning",
    "Artificial Intelligence",
]
