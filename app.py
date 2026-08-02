import logging
from contextlib import asynccontextmanager

from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse

from bot import create_bot_and_dispatcher
from config import config
from database import init_db
from seed import run_seed
from webapp.api import router as api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("majbur-bot")

bot, dp = create_bot_and_dispatcher()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await run_seed()

    if config.BASE_URL and config.BOT_TOKEN:
        webhook_url = f"{config.BASE_URL}/webhook/{config.WEBHOOK_SECRET}"
        try:
            await bot.set_webhook(
                webhook_url,
                drop_pending_updates=True,
                allowed_updates=dp.resolve_used_update_types(),
            )
            logger.info("Webhook o'rnatildi: %s", webhook_url)
        except Exception as e:
            logger.error("Webhook o'rnatishda xatolik: %s", e)
    else:
        logger.warning("BASE_URL yoki BOT_TOKEN sozlanmagan — webhook o'rnatilmadi.")

    yield

    await bot.session.close()


app = FastAPI(title="Majbur Bot + Arenda Mini App", lifespan=lifespan)
app.include_router(api_router)


@app.post("/webhook/{secret}")
async def telegram_webhook(secret: str, request: Request):
    if secret != config.WEBHOOK_SECRET:
        return JSONResponse({"ok": False}, status_code=403)
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/app")
async def serve_miniapp_index():
    return FileResponse("webapp/static/index.html")


@app.get("/app/{filename}")
async def serve_miniapp_asset(filename: str):
    return FileResponse(f"webapp/static/{filename}")
