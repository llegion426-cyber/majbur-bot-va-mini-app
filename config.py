import os
from dataclasses import dataclass, field


def _get_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


@dataclass
class Config:
    # --- Telegram ---
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list = field(default_factory=lambda: [
        int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if x
    ])
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "")  # without @

    GROUP_CHAT_ID: int = int(os.getenv("GROUP_CHAT_ID", "0") or 0)
    CHANNEL_CHAT_ID: int = int(os.getenv("CHANNEL_CHAT_ID", "0") or 0)
    CHANNEL_USERNAME: str = os.getenv("CHANNEL_USERNAME", "")

    BASE_URL: str = os.getenv("BASE_URL", "")
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "majbur-secret")
    PORT: int = int(os.getenv("PORT", "8000"))

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./local.db")

    GROK_API_KEY: str = os.getenv("GROK_API_KEY", "")
    GROK_MODEL: str = os.getenv("GROK_MODEL", "grok-2-latest")
    GROK_API_URL: str = os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions")

    DEFAULT_REQUIRED_INVITES: int = int(os.getenv("DEFAULT_REQUIRED_INVITES", "5"))


config = Config()


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


config.DATABASE_URL = normalize_database_url(config.DATABASE_URL)
