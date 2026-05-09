from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Boolean, Float, ForeignKey, String, Text, UniqueConstraint, text, BigInteger, SmallInteger, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ActiveInactiveStatus, SensorStatus, UserRole
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


class AlertLevel(Base):
    __tablename__ = "alert_levels"

    alert_level: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    alert_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    alert_color: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    alert_events = relationship("AlertEvent", back_populates="alert_level_rel")


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "role in ('super_admin', 'station_admin')",
            name="chk_users_role",
        ),
    )

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(250), nullable=False)

    role: Mapped[UserRole] = mapped_column(String(20), nullable=False)

    station_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("stations.station_id", ondelete="CASCADE"),
        nullable=True,
    )
    is_active: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
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

    station = relationship("Station", back_populates="users")