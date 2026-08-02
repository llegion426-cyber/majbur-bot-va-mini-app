from aiogram import Bot

from config import config


async def is_subscribed_to_channel(bot: Bot, user_id: int) -> bool:
    """CHANNEL_CHAT_ID sozlanmagan bo'lsa, tekshiruv shart emas deb hisoblanadi."""
    if not config.CHANNEL_CHAT_ID:
        return True
    try:
        member = await bot.get_chat_member(chat_id=config.CHANNEL_CHAT_ID, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False
