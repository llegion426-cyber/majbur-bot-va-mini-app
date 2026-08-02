from aiogram import Dispatcher

from bot.handlers import admin_settings, ai_chat, gate, start, user_stats


def register_all_handlers(dp: Dispatcher):
    dp.include_router(start.router)
    dp.include_router(admin_settings.router)
    dp.include_router(user_stats.router)
    dp.include_router(gate.router)
    dp.include_router(ai_chat.router)
