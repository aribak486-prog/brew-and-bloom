from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class MenuItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = Field(default="", max_length=3000)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    image: str = Field(default="", max_length=500)
    rating: Decimal = Field(default=Decimal("5.0"), ge=0, le=5, max_digits=2, decimal_places=1)
    available: bool = True
    category_id: int = Field(gt=0)


class MenuItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=3000)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    image: str | None = Field(default=None, max_length=500)
    rating: Decimal | None = Field(default=None, ge=0, le=5, max_digits=2, decimal_places=1)
    available: bool | None = None
    category_id: int | None = Field(default=None, gt=0)


class AvailabilityUpdate(BaseModel):
    available: bool


class MenuItemPublic(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    image: str
    rating: Decimal
    available: bool
    category_id: int
    category_name: str | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
