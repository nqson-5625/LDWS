from datetime import datetime

from sqlalchemy import DateTime, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SensorType(Base):
    __tablename__ = "sensor_types"

    type_code: Mapped[str] = mapped_column(String(30), primary_key=True)
    type_name: Mapped[str] = mapped_column(String(100), nullable=False)

    unit_1_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    unit_1_symbol: Mapped[str | None] = mapped_column(String(20), nullable=True)
    unit_2_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    unit_2_symbol: Mapped[str | None] = mapped_column(String(20), nullable=True)
    unit_3_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    unit_3_symbol: Mapped[str | None] = mapped_column(String(20), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    sensors = relationship("Sensor", back_populates="sensor_type_rel")
    sensor_readings = relationship("SensorReading", back_populates="sensor_type_rel")