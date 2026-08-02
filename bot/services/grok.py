import httpx

from config import config

SYSTEM_PROMPT = (
    "Sen Telegram botisan. O'zbek tilida, qisqa, do'stona va foydali javob ber. "
    "Agar savol arenda (ijara) uy-joylar haqida bo'lsa, foydalanuvchini botdagi mini ilovadan "
    "(Arenda e'lonlari tugmasi) foydalanishga yo'llat."
)


async def ask_grok(user_text: str) -> str:
    if not config.GROK_API_KEY:
        return "AI xizmati hozircha sozlanmagan. Admin GROK_API_KEY ni kiritishi kerak."

    headers = {
        "Authorization": f"Bearer {config.GROK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.GROK_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(config.GROK_API_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Uzr, AI javob berishda xatolik yuz berdi. ({e})"
