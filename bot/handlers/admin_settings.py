from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from config import config
from database import async_session
from models import BotConfig

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS


async def _update_config(**kwargs) -> BotConfig:
    async with async_session() as session:
        cfg = await session.get(BotConfig, 1)
        if cfg is None:
            cfg = BotConfig(id=1)
            session.add(cfg)
        for key, value in kwargs.items():
            setattr(cfg, key, value)
        await session.commit()
        await session.refresh(cfg)
        return cfg


@router.message(Command("guruh"))
async def cmd_guruh(message: Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    required = config.DEFAULT_REQUIRED_INVITES
    if command.args and command.args.strip().isdigit():
        required = int(command.args.strip())
    await _update_config(group_gate_enabled=True, required_invites=required)
    await message.answer(
        f"✅ Guruhga odam yig'ish sharti YOQILDI.\n"
        f"Foydalanuvchi guruhda yozish uchun kamida <b>{required}</b> kishi taklif qilishi kerak.",
        parse_mode="HTML",
    )


@router.message(Command("guruh_off"))
async def cmd_guruh_off(message: Message):
    if not is_admin(message.from_user.id):
        return
    await _update_config(group_gate_enabled=False)
    await message.answer("❌ Guruhga odam yig'ish sharti O'CHIRILDI.")


@router.message(Command("kanal"))
async def cmd_kanal(message: Message):
    if not is_admin(message.from_user.id):
        return
    if not config.CHANNEL_CHAT_ID:
        await message.answer(
            "⚠️ Avval CHANNEL_CHAT_ID va CHANNEL_USERNAME environment o'zgaruvchilarini sozlang."
        )
        return
    await _update_config(channel_gate_enabled=True)
    await message.answer("✅ Kanalga majburiy obuna sharti YOQILDI.")


@router.message(Command("kanal_off"))
async def cmd_kanal_off(message: Message):
    if not is_admin(message.from_user.id):
        return
    await _update_config(channel_gate_enabled=False)
    await message.answer("❌ Kanalga majburiy obuna sharti O'CHIRILDI.")


@router.message(Command("bal"))
async def cmd_bal(message: Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    points = 1
    if command.args and command.args.strip().isdigit():
        points = int(command.args.strip())
    await _update_config(points_enabled=True, points_per_invite=points)
    await message.answer(
        f"✅ Bal tizimi YOQILDI. Har bir taklif uchun <b>{points}</b> ball beriladi.",
        parse_mode="HTML",
    )


@router.message(Command("bal_off"))
async def cmd_bal_off(message: Message):
    if not is_admin(message.from_user.id):
        return
    await _update_config(points_enabled=False)
    await message.answer("❌ Bal tizimi O'CHIRILDI.")
