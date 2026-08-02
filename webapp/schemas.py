from pydantic import BaseModel


class RegionOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ListingOut(BaseModel):
    id: int
    region_id: int
    title: str
    address: str | None
    price: float
    description: str | None
    photo_base64: str | None
    status: str

    class Config:
        from_attributes = True


class ListingIn(BaseModel):
    region_id: int
    title: str
    address: str | None = None
    price: float = 0
    description: str | None = None
    photo_base64: str | None = None
    status: str = "bosh"  # "bosh" | "band"
