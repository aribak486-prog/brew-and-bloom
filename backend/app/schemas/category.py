from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=3000)
    image: str = Field(default="", max_length=500)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=3000)
    image: str | None = Field(default=None, max_length=500)


class CategoryPublic(BaseModel):
    id: int
    name: str
    description: str
    image: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
