from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, String, BigInteger, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ActiveInactiveStatus
from app.db.base import Base


class Area(Base):
    __tablename__ = "areas"

    __table_args__ = (
        CheckConstraint(
            "status in ('active', 'inactive')",
            name="chk_areas_status",
        ),
    )

    area_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    area_name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[ActiveInactiveStatus] = mapped_column(
        String(20),
        nullable=False,
        default=ActiveInactiveStatus.ACTIVE,
        server_default=text("'active'"),
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

    stations = relationship("Station", back_populates="area", cascade="all, delete-orphan")
    telegram_channel = relationship("TelegramChannel", back_populates="area", uselist=False) # uselist=False -> 1-1
    sensor_readings = relationship("SensorReading", back_populates="area")
    derived_features = relationship("DerivedFeature", back_populates="area")
    alert_events = relationship("AlertEvent", back_populates="area")