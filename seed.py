from sqlalchemy import select

from database import async_session
from models import BotConfig, Region

REGIONS = [
    "Toshkent shahri",
    "Toshkent viloyati",
    "Andijon",
    "Farg'ona",
    "Namangan",
    "Sirdaryo",
    "Jizzax",
    "Samarqand",
    "Buxoro",
    "Navoiy",
    "Qashqadaryo",
    "Surxondaryo",
    "Xorazm",
    "Qoraqalpog'iston",
]


async def seed_regions():
    async with async_session() as session:
        result = await session.execute(select(Region))
        existing = {r.name for r in result.scalars().all()}
        added = False
        for i, name in enumerate(REGIONS):
            if name not in existing:
                session.add(Region(name=name, order=i))
                added = True
        if added:
            await session.commit()


async def seed_config():
    async with async_session() as session:
        cfg = await session.get(BotConfig, 1)
        if cfg is None:
            session.add(BotConfig(id=1))
            await session.commit()


async def run_seed():
    await seed_regions()
    await seed_config()
