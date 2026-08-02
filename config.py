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

    # Group that gets "gated" (foydalanuvchi N kishi taklif qilmaguncha yoza olmaydi)
    GROUP_CHAT_ID: int = int(os.getenv("GROUP_CHAT_ID", "0") or 0)
    # Channel that must be subscribed to (majburiy obuna)
    CHANNEL_CHAT_ID: int = int(os.getenv("CHANNEL_CHAT_ID", "0") or 0)
    CHANNEL_USERNAME: str = os.getenv("CHANNEL_USERNAME", "")  # without @, used for invite link text

    # --- Web / deploy ---
    BASE_URL: str = os.getenv("BASE_URL", "")  # e.g. https://your-app.up.railway.app
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "majbur-secret")
    PORT: int = int(os.getenv("PORT", "8000"))

    # --- Database ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./local.db")

    # --- AI (standart: Groq, OpenAI-mos endpoint orqali, bepul) ---
    GROK_API_KEY: str = os.getenv("GROK_API_KEY", "")
    GROK_MODEL: str = os.getenv("GROK_MODEL", "llama-3.3-70b-versatile")
    GROK_API_URL: str = os.getenv(
        "GROK_API_URL", "https://api.groq.com/openai/v1/chat/completions"
    )

    # --- Defaults for gate settings (overridable later from DB via /guruh /kanal /bal) ---
    DEFAULT_REQUIRED_INVITES: int = int(os.getenv("DEFAULT_REQUIRED_INVITES", "5"))


config = Config()


def normalize_database_url(url: str) -> str:
    """Render/Railway odatda postgres:// beradi, SQLAlchemy async uchun postgresql+asyncpg:// kerak."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


config.DATABASE_URL = normalize_database_url(config.DATABASE_URL)
