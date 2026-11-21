

import uuid

from pydantic import BaseModel
from sqlalchemy import UUID, Column, Float, Integer, String, Enum, Boolean, Text, false
from sqlalchemy.orm import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

class ProductStatus(PyEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)  # Также можно использовать Float
    count = Column(Integer, nullable=False)
    description = Column(Text, nullable=False, server_default="")
    status = Column(Enum(ProductStatus, name="product_status"), nullable=False, server_default=ProductStatus.DRAFT.name)
    is_featured = Column(Boolean, nullable=False, server_default=false())


# Pydantic модель для валидации входных данных
class ProductCreate(BaseModel):
    title: str
    price: float
    count: int
    description: str


class CustomExceptionModel(BaseModel):

    status_code: int
    er_message: str
    er_details: str    