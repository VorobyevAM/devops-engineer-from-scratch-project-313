import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    database_url: str
    base_url: str | None
    sentry_dsn: str | None


def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./app.db"),
        base_url=os.getenv("BASE_URL"),
        sentry_dsn=os.getenv("SENTRY_DSN"),
    )
