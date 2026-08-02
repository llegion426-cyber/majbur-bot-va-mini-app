import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    invited_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    invites_count: Mapped[int] = mapped_column(Integer, default=0)
    points: Mapped[int] = mapped_column(Integer, default=0)

    is_unlocked: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_channel: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    order: Mapped[int] = mapped_column(Integer, default=0)

    listings: Mapped[list["Listing"]] = relationship(back_populates="region")


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"))
    title: Mapped[str] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_base64: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="bosh")

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    region: Mapped["Region"] = relationship(back_populates="listings")


class BotConfig(Base):
    __tablename__ = "bot_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    group_gate_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    channel_gate_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    points_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    required_invites: Mapped[int] = mapped_column(Integer, default=5)
    points_per_invite: Mapped[int] = mapped_column(Integer, default=1)
