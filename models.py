from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class Clan(Base):
    __tablename__ = "clans"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),  # requires pgcrypto
    )
    name = Column(String(255), nullable=False)
    region = Column(String(4), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("timezone('utc', now())"),
    )
