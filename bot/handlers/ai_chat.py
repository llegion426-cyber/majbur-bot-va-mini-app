from aiogram import Bot, F, Router
from aiogram.types import Message

from bot.services.grok import ask_grok
from config import config

router = Router()


@router.message(F.chat.type == "private", F.text, ~F.text.startswith("/"))
async def on_private_text(message: Message, bot: Bot):
    if message.from_user.id in config.ADMIN_IDS:
        await message.answer("👑 Salom, xo'jayin! Sizga qanday yordam bera olaman?")
        return

    await bot.send_chat_action(message.chat.id, "typing")
    answer = await ask_grok(message.text)
    await message.answer(answer)
