from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message

from bot.keyboards import channel_subscribe_kb, main_menu_kb
from bot.services.referral import get_or_create_user, register_referral, try_unlock_group_member
from bot.services.subscription import is_subscribed_to_channel
from config import config

router = Router()

HELP_TEXT = (
    "🔧 <b>Bot buyruqlari</b>\n\n"
    "/start — botni ishga tushirish\n"
    "/help — qo'llanma\n"
    "/meni — siz qo'shgan odamlar soni\n"
    "/sizni — biror foydalanuvchining taklif sonini ko'rish (xabarga javob qilib yuboring)\n"
    "/top — eng ko'p taklif qilganlar reytingi\n\n"
    "👑 <b>Admin buyruqlari</b>\n"
    "/guruh, /guruh_off — guruhga odam yig'ish shartini yoqish/o'chirish\n"
    "/kanal, /kanal_off — kanalga obuna shartini yoqish/o'chirish\n"
    "/bal — bal (ballar) tizimini yoqish/o'chirish"
)


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, bot: Bot):
    user = message.from_user
    await get_or_create_user(user.id, user.username, user.full_name)

    payload = command.args
    if payload and payload.startswith("ref_"):
        try:
            inviter_id = int(payload.replace("ref_", ""))
            counted = await register_referral(user.id, inviter_id)
            if counted:
                await try_unlock_group_member(bot, config.GROUP_CHAT_ID, inviter_id)
                try:
                    await bot.send_message(
                        inviter_id,
                        f"🎉 Siz orqali <b>{user.full_name}</b> botga qo'shildi! "
                        f"Taklif qilganlaringiz sonini /meni buyrug'i orqali ko'rishingiz mumkin.",
                        parse_mode="HTML",
                    )
                except Exception:
                    pass
        except ValueError:
            pass

    if config.CHANNEL_CHAT_ID and not await is_subscribed_to_channel(bot, user.id):
        await message.answer(
            "👋 Xush kelibsiz!\n\n"
            "Botdan foydalanishdan oldin quyidagi kanalga obuna bo'lishingiz kerak:",
            reply_markup=channel_subscribe_kb(),
        )
        return

    await message.answer(
        f"👋 Assalomu alaykum, <b>{user.full_name}</b>!\n\n"
        "Bu bot orqali do'stlaringizni taklif qilib, guruhga yozish huquqini ochishingiz "
        "va arenda (ijara) e'lonlarini mini ilova orqali ko'rishingiz mumkin.\n\n"
        "Quyidagi tugmalardan birini tanlang 👇",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


@router.callback_query(F.data == "check_sub")
async def cb_check_sub(call: CallbackQuery, bot: Bot):
    if await is_subscribed_to_channel(bot, call.from_user.id):
        await call.message.edit_text("✅ Rahmat! Endi botdan to'liq foydalanishingiz mumkin.")
        await call.message.answer("Asosiy menyu 👇", reply_markup=main_menu_kb())
    else:
        await call.answer("❌ Siz hali kanalga obuna bo'lmadingiz!", show_alert=True)


@router.callback_query(F.data == "start_action")
async def cb_start_action(call: CallbackQuery, bot: Bot):
    user_id = call.from_user.id
    link = f"https://t.me/{config.BOT_USERNAME}?start=ref_{user_id}" if config.BOT_USERNAME else "(BOT_USERNAME sozlanmagan)"
    await call.message.answer(
        "🔗 Sizning shaxsiy taklif havolangiz:\n"
        f"<code>{link}</code>\n\n"
        "Ushbu havola orqali kirgan har bir do'stingiz sizning hisobingizga +1 bo'lib qo'shiladi.",
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data == "help_action")
async def cb_help_action(call: CallbackQuery):
    await call.message.answer(HELP_TEXT, parse_mode="HTML")
    await call.answer()


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, parse_mode="HTML")
