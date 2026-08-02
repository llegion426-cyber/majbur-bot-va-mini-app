from aiogram import Bot
from aiogram.types import ChatPermissions
from sqlalchemy import select

from database import async_session
from models import BotConfig, User


async def get_or_create_user(user_id: int, username: str | None, full_name: str | None) -> User:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user is None:
            user = User(id=user_id, username=username, full_name=full_name)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        else:
            changed = False
            if username and user.username != username:
                user.username = username
                changed = True
            if full_name and user.full_name != full_name:
                user.full_name = full_name
                changed = True
            if changed:
                await session.commit()
        return user


async def get_config() -> BotConfig:
    async with async_session() as session:
        cfg = await session.get(BotConfig, 1)
        if cfg is None:
            cfg = BotConfig(id=1)
            session.add(cfg)
            await session.commit()
            await session.refresh(cfg)
        return cfg


async def register_referral(new_user_id: int, inviter_id: int) -> bool:
    """Yangi foydalanuvchi birinchi marta /start bosganda, taklif qilgan odamga +1 hisoblanadi.
    Qaytaradi: True — hisoblandi, False — hisoblanmadi (masalan o'zini o'zi taklif qilgan yoki avval hisoblangan)."""
    if new_user_id == inviter_id:
        return False

    async with async_session() as session:
        new_user = await session.get(User, new_user_id)
        if new_user is not None and new_user.invited_by is not None:
            return False

        inviter = await session.get(User, inviter_id)
        if inviter is None:
            return False

        if new_user is None:
            new_user = User(id=new_user_id, invited_by=inviter_id)
            session.add(new_user)
        else:
            new_user.invited_by = inviter_id

        inviter.invites_count += 1

        cfg = await session.get(BotConfig, 1)
        if cfg and cfg.points_enabled:
            inviter.points += cfg.points_per_invite

        await session.commit()
        return True


async def get_stats(user_id: int) -> User | None:
    async with async_session() as session:
        return await session.get(User, user_id)


async def get_top(limit: int = 10) -> list[User]:
    async with async_session() as session:
        result = await session.execute(select(User).order_by(User.invites_count.desc()).limit(limit))
        return list(result.scalars().all())


async def try_unlock_group_member(bot: Bot, group_chat_id: int, user_id: int) -> None:
    """Foydalanuvchi yetarlicha odam taklif qilgan bo'lsa, guruhda yozish huquqini ochib beradi."""
    if not group_chat_id:
        return
    async with async_session() as session:
        user = await session.get(User, user_id)
        cfg = await session.get(BotConfig, 1)
        if not user or not cfg or not cfg.group_gate_enabled:
            return
        if user.invites_count >= cfg.required_invites and not user.is_unlocked:
            try:
                await bot.restrict_chat_member(
                    chat_id=group_chat_id,
                    user_id=user_id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_photos=True,
                        can_send_videos=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                    ),
                )
                user.is_unlocked = True
                await session.commit()
            except Exception:
                pass
