from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AlertLevel


class AlertLevelRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_level(self, alert_level: int) -> AlertLevel | None:
        stmt = select(AlertLevel).where(AlertLevel.alert_level == alert_level)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_name(self, alert_name: str) -> AlertLevel | None:
        stmt = select(AlertLevel).where(AlertLevel.alert_name == alert_name)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_all(self) -> list[AlertLevel]:
        stmt = select(AlertLevel).order_by(AlertLevel.alert_level.asc())
        return list(self.db.execute(stmt).scalars().all())
    
    def create(self, **kwargs) -> AlertLevel:
        alert_level = AlertLevel(**kwargs)
        try:
            self.db.add(alert_level)
            self.db.flush()
            self.db.refresh(alert_level)
            self.db.commit()
            return alert_level
        except Exception:
            self.db.rollback()
            raise

    def update(self, alert_level_obj: AlertLevel, **kwargs) -> AlertLevel:
        try:
            for key, value in kwargs.items():
                setattr(alert_level_obj, key, value)
            self.db.add(alert_level_obj)
            self.db.flush()
            self.db.refresh(alert_level_obj)
            self.db.commit()
            return alert_level_obj
        except Exception:
            self.db.rollback()
            raise

    def delete(self, alert_level_obj: AlertLevel) -> None:
        try:
            self.db.delete(alert_level_obj)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise