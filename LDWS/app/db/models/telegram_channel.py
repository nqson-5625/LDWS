from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, BigInteger, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TelegramChannel(Base):
    __tablename__ = "telegram_channels"

    channel_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    area_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("areas.area_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    channel_name: Mapped[str] = mapped_column(String(150), nullable=False)
    telegram_chat_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    channel_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    qr_code_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    area = relationship("Area", back_populates="telegram_channel")