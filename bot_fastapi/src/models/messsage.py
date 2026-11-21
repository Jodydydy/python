

from pydantic import BaseModel
from sqlalchemy import BIGINT, Column, ForeignKey, Identity, String, Text, TIMESTAMP, func
from models.base import Base
from sqlalchemy.orm import relationship


class Message(Base):
    __tablename__ = "messages"

    id = Column(BIGINT, Identity(always=True), primary_key=True)
    user_id = Column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    user = relationship("User", back_populates="messages")


class MessageRequest(BaseModel):
    user_id: int 
    username: str
    text: str


