from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint, BigInteger, SmallInteger, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Float

from app.core.enums import AlertEventType
from app.db.base import Base


class AlertEvent(Base):
    __tablename__ = "alert_events"

    __table_args__ = (
        PrimaryKeyConstraint("event_id", "timestamp", name="pk_alert_events"),
        CheckConstraint(
            "event_type in ('created', 'upgraded', 'downgraded', 'resolved')",
            name="chk_alert_event_type",
        ),
        Index("idx_alert_events_area_time", "area_id", text('"timestamp" DESC')),
        Index("idx_alert_events_station_time", "station_id", text('"timestamp" DESC')),
    )

    event_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    area_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("areas.area_id", ondelete="CASCADE"),
        nullable=False,
    )
    station_id: Mapped[int] = mapped_column(
        ForeignKey("stations.station_id", ondelete="CASCADE"),
        nullable=False,
    )
    alert_level: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("alert_levels.alert_level"),
        nullable=False,
    )
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    trigger_feature_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    trigger_feature_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    alert_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    event_type: Mapped[AlertEventType] = mapped_column(String(20), nullable=False)

    telegram_sent: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    telegram_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    area = relationship("Area", back_populates="alert_events")
    station = relationship("Station", back_populates="alert_events")
    alert_level_rel = relationship("AlertLevel", back_populates="alert_events")
    alert_status_records = relationship("AlertStatus", back_populates="latest_event")


class AlertStatus(Base):
    __tablename__ = "alert_status"

    __table_args__ = (
        PrimaryKeyConstraint("station_id", name="pk_alert_status"),
        ForeignKeyConstraint(
            ["latest_event_id", "latest_event_timestamp"],
            ["alert_events.event_id", "alert_events.timestamp"],
            name="fk_alert_status_event",
            ondelete="CASCADE",
        ),
        Index("idx_alert_status_latest_event", "latest_event_id", "latest_event_timestamp", unique=True),
    )

    station_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stations.station_id", ondelete="CASCADE"),
        nullable=False,
    )

    latest_event_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    latest_event_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    station = relationship("Station", back_populates="alert_status")
    latest_event = relationship(
        "AlertEvent",
        back_populates="alert_status_records",
        foreign_keys=[latest_event_id, latest_event_timestamp],
    )