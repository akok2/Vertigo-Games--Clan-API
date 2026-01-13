from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ClanIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    region: str = Field(..., min_length=2, max_length=4, description="Region code, e.g. TR, US")


class ClanCreateResponse(BaseModel):
    id: UUID
    message: str


class ClanDeleteResponse(BaseModel):
    id: UUID
    message: str


class ClanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    region: str
    created_at: datetime


# Optional: schema for search query validation (min 3 letters)
class ClanNameSearch(BaseModel):
    name: str = Field(..., min_length=3, description="Min 3 letters, contains search")
