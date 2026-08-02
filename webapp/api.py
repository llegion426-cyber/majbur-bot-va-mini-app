from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import select

from database import async_session
from models import Listing, Region
from webapp.schemas import ListingIn, ListingOut, RegionOut
from webapp.telegram_auth import is_admin_init_data, validate_init_data

router = APIRouter(prefix="/api")


def _require_admin(x_telegram_init_data: str | None):
    if not x_telegram_init_data or not is_admin_init_data(x_telegram_init_data):
        raise HTTPException(status_code=403, detail="Faqat admin uchun ruxsat berilgan")


@router.get("/me")
async def me(x_telegram_init_data: str | None = Header(default=None)):
    data = validate_init_data(x_telegram_init_data or "")
    if not data:
        raise HTTPException(status_code=401, detail="Noto'g'ri initData")
    user = data.get("user", {})
    from config import config

    return {"id": user.get("id"), "is_admin": user.get("id") in config.ADMIN_IDS}


@router.get("/regions", response_model=list[RegionOut])
async def list_regions():
    async with async_session() as session:
        result = await session.execute(select(Region).order_by(Region.order))
        return list(result.scalars().all())


@router.get("/listings", response_model=list[ListingOut])
async def list_listings(region_id: int | None = None):
    async with async_session() as session:
        stmt = select(Listing).order_by(Listing.created_at.desc())
        if region_id:
            stmt = stmt.where(Listing.region_id == region_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())


@router.get("/listings/{listing_id}", response_model=ListingOut)
async def get_listing(listing_id: int):
    async with async_session() as session:
        listing = await session.get(Listing, listing_id)
        if not listing:
            raise HTTPException(status_code=404, detail="Topilmadi")
        return listing


@router.post("/admin/listings", response_model=ListingOut)
async def create_listing(payload: ListingIn, x_telegram_init_data: str | None = Header(default=None)):
    _require_admin(x_telegram_init_data)
    async with async_session() as session:
        listing = Listing(**payload.model_dump())
        session.add(listing)
        await session.commit()
        await session.refresh(listing)
        return listing


@router.put("/admin/listings/{listing_id}", response_model=ListingOut)
async def update_listing(
    listing_id: int, payload: ListingIn, x_telegram_init_data: str | None = Header(default=None)
):
    _require_admin(x_telegram_init_data)
    async with async_session() as session:
        listing = await session.get(Listing, listing_id)
        if not listing:
            raise HTTPException(status_code=404, detail="Topilmadi")
        for key, value in payload.model_dump().items():
            setattr(listing, key, value)
        await session.commit()
        await session.refresh(listing)
        return listing


@router.delete("/admin/listings/{listing_id}")
async def delete_listing(listing_id: int, x_telegram_init_data: str | None = Header(default=None)):
    _require_admin(x_telegram_init_data)
    async with async_session() as session:
        listing = await session.get(Listing, listing_id)
        if not listing:
            raise HTTPException(status_code=404, detail="Topilmadi")
        await session.delete(listing)
        await session.commit()
        return {"ok": True}
