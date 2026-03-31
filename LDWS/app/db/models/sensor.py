from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, text, BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import SensorStatus
from app.db.base import Base


class Sensor(Base):
    __tablename__ = "sensors"

    __table_args__ = (
        CheckConstraint(
            "status in ('active', 'inactive', 'maintenance')",
            name="chk_sensors_status",
        ),
        Index("idx_sensors_station_id", "station_id"),
        Index("idx_sensors_type_code", "type_code"),
    )

    sensor_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    station_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stations.station_id", ondelete="CASCADE"),
        nullable=False,
    )
    type_code: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("sensor_types.type_code", ondelete="RESTRICT"),
        nullable=False,
    )
    sensor_code: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    sensor_name: Mapped[str] = mapped_column(String(150), nullable=False)
    install_position: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[SensorStatus] = mapped_column(
        String(20),
        nullable=False,
        default=SensorStatus.ACTIVE,
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

    station = relationship("Station", back_populates="sensors")
    sensor_type_rel = relationship("SensorType", back_populates="sensors")
    sensor_readings = relationship("SensorReading", back_populates="sensor")