from sqlalchemy import String, Text, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AlertLevel(Base):
    __tablename__ = "alert_levels"

    alert_level: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    alert_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    alert_color: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    alert_events = relationship("AlertEvent", back_populates="alert_level_rel")