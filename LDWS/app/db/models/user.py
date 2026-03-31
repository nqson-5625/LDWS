from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, BigInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import UserRole
from app.db.base import Base


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