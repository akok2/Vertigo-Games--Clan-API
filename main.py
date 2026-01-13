import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from models import Base, Clan
from schemas import ClanIn, ClanOut, ClanCreateResponse, ClanDeleteResponse


def build_db_url() -> str:
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "postgres")

    missing = [k for k, v in {"DB_USER": user, "DB_PASSWORD": password, "DB_HOST": host}.items() if not v]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"


DB_URL = build_db_url()

engine = create_async_engine(DB_URL, echo=False)  # keep logs cleaner for reviewers
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except OperationalError as e:
        # Cloud Run logs will show this clearly
        raise RuntimeError(f"Database connection failed: {e}") from e

    yield
    await engine.dispose()


app = FastAPI(
    title="Vertigo Games - Clan API",
    version="1.0.0",
    lifespan=lifespan,
)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@app.get("/health")
async def health():
    return {"status": "ok"}


# POST /clans -> create clan
@app.post("/clans", response_model=ClanCreateResponse, status_code=201)
async def create_clan(clan: ClanIn, db: AsyncSession = Depends(get_db)):
    new_clan = Clan(**clan.model_dump())
    db.add(new_clan)
    await db.commit()
    await db.refresh(new_clan)

    return {
        "id": str(new_clan.id),
        "message": "Clan created successfully.",
    }


# GET /clans -> list all clans (optional region filter; stable ordering)
@app.get("/clans", response_model=List[ClanOut])
async def list_clans(
    region: Optional[str] = Query(None, description="Filter clans by region (e.g. TR, US)"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Clan)

    if region:
        stmt = stmt.where(Clan.region == region)

    stmt = stmt.order_by(desc(Clan.created_at))

    result = await db.execute(stmt)
    return result.scalars().all()


# GET /clans/search?name=abc -> contains search, min 3 letters
@app.get("/clans/search", response_model=List[ClanOut])
async def search_clans(
    name: str = Query(..., min_length=3, description="Clan name search (min 3 chars, contains)"),
    db: AsyncSession = Depends(get_db),
):
    # Case-insensitive contains
    stmt = select(Clan).where(Clan.name.ilike(f"%{name}%")).order_by(desc(Clan.created_at))
    result = await db.execute(stmt)
    return result.scalars().all()


# DELETE /clans/{clan_id} -> delete clan
@app.delete("/clans/{clan_id}", response_model=ClanDeleteResponse)
async def delete_clan(clan_id: str, db: AsyncSession = Depends(get_db)):
    clan = await db.get(Clan, clan_id)
    if not clan:
        raise HTTPException(status_code=404, detail="Clan not found")

    await db.delete(clan)
    await db.commit()

    return {
        "id": str(clan.id),
        "message": "Clan deleted successfully.",
    }
