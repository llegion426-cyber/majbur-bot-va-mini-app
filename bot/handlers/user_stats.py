from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.services.referral import get_config, get_stats, get_top

router = Router()


@router.message(Command("meni"))
async def cmd_meni(message: Message):
    user = await get_stats(message.from_user.id)
    cfg = await get_config()
    invites = user.invites_count if user else 0
    points = user.points if user else 0

    text = f"🈁 Siz jami <b>{invites}</b> ta odam qo'shgansiz!"
    if cfg.group_gate_enabled:
        left = max(cfg.required_invites - invites, 0)
        if left > 0:
            text += f"\nGuruhga yozish uchun yana <b>{left}</b> kishi kerak."
        else:
            text += "\n✅ Guruhga yozish huquqi ochiq."
    if cfg.points_enabled:
        text += f"\n🎁 Ballaringiz: <b>{points}</b>"

    await message.answer(text, parse_mode="HTML")


@router.message(Command("sizni"))
async def cmd_sizni(message: Message):
    if not message.reply_to_message:
        await message.answer(
            "ℹ️ Kimningdir taklif sonini ko'rish uchun ushbu buyruqni o'sha odamning "
            "xabariga javob (reply) qilib yuboring."
        )
        return
    target = message.reply_to_message.from_user
    user = await get_stats(target.id)
    invites = user.invites_count if user else 0
    await message.answer(
        f"📊 <b>{target.full_name}</b>ning guruhga qo'shgan odamlar soni: <b>{invites}</b>",
        parse_mode="HTML",
    )


@router.message(Command("top"))
async def cmd_top(message: Message):
    top_users = await get_top(10)
    if not top_users:
        await message.answer("Hozircha hech kim odam taklif qilmagan.")
        return

    lines = ["🏆 <b>Top 10 taklif qiluvchilar</b>\n"]
    medals = ["🥇", "🥈", "🥉"]
    for i, u in enumerate(top_users):
        medal = medals[i] if i < 3 else f"{i + 1}."
        name = u.full_name or u.username or str(u.id)
        lines.append(f"{medal} {name} — <b>{u.invites_count}</b> ta")

    await message.answer("\n".join(lines), parse_mode="HTML")
