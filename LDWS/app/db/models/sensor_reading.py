from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, PrimaryKeyConstraint, BigInteger, SmallInteger, Index, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Float, String

from app.db.base import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    __table_args__ = (
        PrimaryKeyConstraint("reading_id", "timestamp", name="pk_sensor_readings"),
        CheckConstraint(
            "quality_flag in (0, 1, 2, 3, 4)",
            name="chk_sensor_readings_quality_flag",
        ),
        Index("idx_sensor_readings_station_time", "station_id", text('"timestamp" DESC')),
        Index("idx_sensor_readings_area_time", "area_id", text('"timestamp" DESC')),
        Index("idx_sensor_readings_sensor_time", "sensor_id", text('"timestamp" DESC')),
        Index("idx_sensor_readings_type_time", "sensor_type", text('"timestamp" DESC')),
    )

    reading_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    area_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("areas.area_id", ondelete="CASCADE"),
        nullable=False,
    )
    station_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stations.station_id", ondelete="CASCADE"),
        nullable=False,
    )
    sensor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("sensors.sensor_id", ondelete="CASCADE"),
        nullable=False,
    )
    sensor_type: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("sensor_types.type_code", ondelete="RESTRICT"),
        nullable=False,
    )

    value_1: Mapped[float | None] = mapped_column(Float, nullable=True)
    value_2: Mapped[float | None] = mapped_column(Float, nullable=True)
    value_3: Mapped[float | None] = mapped_column(Float, nullable=True)

    quality_flag: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        server_default=text("0"),
    )
    raw_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    area = relationship("Area", back_populates="sensor_readings")
    station = relationship("Station", back_populates="sensor_readings")
    sensor = relationship("Sensor", back_populates="sensor_readings")
    sensor_type_rel = relationship("SensorType", back_populates="sensor_readings")