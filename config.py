"""Configuration loader — reads .env and exposes settings."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    DIGEST_HOUR: int = int(os.getenv("DIGEST_HOUR", "9"))
    DIGEST_MINUTE: int = int(os.getenv("DIGEST_MINUTE", "0"))
    RUN_ON_START: bool = os.getenv("RUN_ON_START", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DB_PATH: str = os.getenv("DB_PATH", "data/startups.db")
    USER_AGENT: str = (
        "StartupMonitorBot/1.0 "
        "(+https://github.com/startup-monitor; educational project)"
    )

    @classmethod
    def validate(cls) -> list[str]:
        errors = []
        if not cls.TELEGRAM_BOT_TOKEN or cls.TELEGRAM_BOT_TOKEN == "your_bot_token_here":
            errors.append("TELEGRAM_BOT_TOKEN is not set")
        if not cls.TELEGRAM_CHAT_ID or cls.TELEGRAM_CHAT_ID == "your_chat_id_here":
            errors.append("TELEGRAM_CHAT_ID is not set")
        return errors
