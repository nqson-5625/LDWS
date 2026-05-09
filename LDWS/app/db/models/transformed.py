from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, PrimaryKeyConstraint, BigInteger, SmallInteger, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Float

from app.db.base import Base


class DerivedFeature(Base):
    __tablename__ = "derived_features"

    __table_args__ = (
        PrimaryKeyConstraint("feature_id", "timestamp", name="pk_derived_features"),
        CheckConstraint(
            "alert_level_candidate is null or alert_level_candidate in (1, 2, 3, 4, 5)",
            name="chk_derived_features_alert_level",
        ),
        Index("idx_derived_features_area_time", "area_id", text('"timestamp" DESC')),
        Index("idx_derived_features_station_time", "station_id", text('"timestamp" DESC')),
    )

    feature_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

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

    rain_1h: Mapped[float | None] = mapped_column(Float, nullable=True)
    rain_3h: Mapped[float | None] = mapped_column(Float, nullable=True)
    rain_24h: Mapped[float | None] = mapped_column(Float, nullable=True)
    rain_3d: Mapped[float | None] = mapped_column(Float, nullable=True)
    rain_intensity: Mapped[float | None] = mapped_column(Float, nullable=True)

    tilt_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    tilt_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    tilt_change_1h: Mapped[float | None] = mapped_column(Float, nullable=True)
    tilt_change_24h: Mapped[float | None] = mapped_column(Float, nullable=True)

    disp_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    disp_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    disp_change_1h: Mapped[float | None] = mapped_column(Float, nullable=True)
    disp_change_24h: Mapped[float | None] = mapped_column(Float, nullable=True)

    vibration_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    vibration_peak: Mapped[float | None] = mapped_column(Float, nullable=True)
    vibration_flag: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=False,
        server_default=text("false"),
    )

    temperature_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature_flag: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=False,
        server_default=text("false"),
    )

    anomaly_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    anomaly_flag: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    alert_level_candidate: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    area = relationship("Area", back_populates="derived_features")
    station = relationship("Station", back_populates="derived_features")