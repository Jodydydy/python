

import uuid

from pydantic import BaseModel
from sqlalchemy import UUID, Column, Float, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)  # Также можно использовать Float
    count = Column(Integer, nullable=False)
    description = Column(String, nullable=False, server_default="")


# Pydantic модель для валидации входных данных
class ProductCreate(BaseModel):
    title: str
    price: float
    count: int
    description: str