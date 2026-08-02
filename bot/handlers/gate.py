from aiogram import Bot, Router
from aiogram.types import ChatMemberUpdated, ChatPermissions

from bot.services.referral import get_config, get_or_create_user
from config import config

router = Router()


@router.chat_member()
async def on_chat_member_update(event: ChatMemberUpdated, bot: Bot):
    if event.chat.id != config.GROUP_CHAT_ID:
        return
    if event.new_chat_member.status != "member":
        return
    if event.old_chat_member.status in ("member", "administrator", "creator"):
        return

    user = event.new_chat_member.user
    if user.is_bot:
        return

    db_user = await get_or_create_user(user.id, user.username, user.full_name)
    cfg = await get_config()

    if not cfg.group_gate_enabled:
        return
    if db_user.invites_count >= cfg.required_invites:
        return

    try:
        await bot.restrict_chat_member(
            chat_id=event.chat.id,
            user_id=user.id,
            permissions=ChatPermissions(can_send_messages=False),
        )
        left = cfg.required_invites - db_user.invites_count
        await bot.send_message(
            event.chat.id,
            f"👋 {user.full_name}, guruhda yozish uchun avval botga o'ting va kamida "
            f"<b>{left}</b> kishini taklif qiling. Taklif havolangizni /start orqali oling.",
            parse_mode="HTML",
        )
    except Exception:
        pass
