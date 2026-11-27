import datetime

from sqlalchemy import BIGINT, Column, String, TIMESTAMP, func
from models.base import Base
from sqlalchemy.orm import relationship

CONTEXT_LIMITS = ["short", "normal", "long"]
context_mode = {"short": 4, "normal": 10, "long": 25}

class User(Base):
    __tablename__ = "users"

    id = Column(BIGINT, primary_key=True)
    username = Column(String(255))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    context_mode = Column(String(10))
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")

 

