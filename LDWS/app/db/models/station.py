from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, String, Text, UniqueConstraint, text, BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ActiveInactiveStatus
from app.db.base import Base


class Station(Base):
    __tablename__ = "stations"

    __table_args__ = (
        UniqueConstraint("area_id", "station_name", name="uq_station_name_per_area"),
        CheckConstraint(
            "status in ('active', 'inactive')",
            name="chk_stations_status",
        ),
        Index("idx_stations_area_id", "area_id"),
    )

    station_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    area_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("areas.area_id", ondelete="CASCADE"),
        nullable=False,
    )

    station_name: Mapped[str] = mapped_column(String(150), nullable=False)
    location_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    elevation: Mapped[float | None] = mapped_column(Float, nullable=True)

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

    area = relationship("Area", back_populates="stations")
    users = relationship("User", back_populates="station")
    sensors = relationship("Sensor", back_populates="station", cascade="all, delete-orphan")
    sensor_readings = relationship("SensorReading", back_populates="station")
    derived_features = relationship("DerivedFeature", back_populates="station")
    alert_events = relationship("AlertEvent", back_populates="station")
    alert_status = relationship("AlertStatus", back_populates="station", uselist=False) # 1-1