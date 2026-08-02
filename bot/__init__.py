from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.handlers import register_all_handlers
from config import config


def create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    register_all_handlers(dp)
    return bot, dp
