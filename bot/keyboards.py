from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from config import config


def main_menu_kb() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="✅ Boshlash", callback_data="start_action"),
            InlineKeyboardButton(text="📖 Qo'llanma", callback_data="help_action"),
        ]
    ]
    if config.BASE_URL:
        rows.append(
            [InlineKeyboardButton(text="🏠 Arenda e'lonlari", web_app=WebAppInfo(url=config.BASE_URL + "/app"))]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def channel_subscribe_kb() -> InlineKeyboardMarkup:
    rows = []
    if config.CHANNEL_USERNAME:
        rows.append(
            [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=f"https://t.me/{config.CHANNEL_USERNAME}")]
        )
    rows.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def share_link_kb(link: str, text: str) -> InlineKeyboardMarkup:
    share_url = f"https://t.me/share/url?url={link}&text={text}"
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📤 Do'stlarga ulashish", url=share_url)]]
    )
