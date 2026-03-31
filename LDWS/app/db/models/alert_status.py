from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint, BigInteger, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


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