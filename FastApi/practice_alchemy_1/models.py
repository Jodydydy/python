from typing import Literal

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel, ConfigDict, Field

class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    price: Mapped[int]
    count: Mapped[int]


class ProductCreate(BaseModel):

    title: str
    price: int
    count: int


class ProductResponse(ProductCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)        


class ProductFilter(BaseModel):

    min_price: int | None = Field(default=None, ge=0)
    max_price: int | None = Field(default=None, ge=0)
    title: str | None = None
    in_stock: bool = False

    sort_by: Literal["id", "title", "price", "count"] = "id"
    order: Literal["asc", "desc"] = "asc"
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ProductPage(BaseModel):
    items: list[ProductResponse]
    total: int
    limit: int
    offset: int
    has_next: bool


class CustomExceptionModel(BaseModel):

    status_code: int
    er_message: str
    er_details: str       