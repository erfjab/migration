from datetime import datetime
from sqlalchemy import Integer, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from db import Base


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
