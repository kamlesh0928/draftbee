import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    # Current Date
    DATE: str = datetime.datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).date().isoformat()

    # Database
    DATABASE_URL: str

    # Discord
    DISCORD_BOT_TOKEN: str
    DISCORD_SERVER_ID: int

    # Gemini
    GEMINI_API_KEY: str


settings = Settings()

TOPICS = [
    "Data Structures and Algorithms",
    "System Design",
    "Full Stack Development",
    "Machine Learning",
    "Artificial Intelligence",
]
