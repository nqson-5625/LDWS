from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Station

class StationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, station_id: int) -> Station | None:
        stmt = select(Station).where(Station.station_id == station_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_area_and_name(self, area_id: int, station_name: str) -> Station | None:
        stmt = select(Station).where(
            Station.area_id == area_id,
            Station.station_name == station_name
        )
        return self.db.execute(stmt).scalar_one_or_none()
    
    def list_all(self) -> list[Station]:
        stmt = select(Station).order_by(Station.station_id.asc())
        return list(self.db.execute(stmt).scalars().all())
    
    def list_by_area(self, area_id: int) -> list[Station]:
        stmt = select(Station).where(Station.area_id == area_id).order_by(Station.station_id.asc())
        return list(self.db.execute(stmt).scalars().all())
    
    def create(self, **kwargs) -> Station:
        station = Station(**kwargs)

        try:
            self.db.add(station)
            self.db.flush()
            self.db.refresh(station)
            self.db.commit()
            return station
        except Exception:
            self.db.rollback()
            raise

    def update(self, station: Station, **kwargs) -> Station:
        try:
            for key, value in kwargs.items():
                setattr(station, key, value)

            self.db.add(station)
            self.db.flush()
            self.db.refresh(station)
            self.db.commit()
            return station
        except Exception:
            self.db.rollback()
            raise

    def delete(self, station: Station) -> None:
        try:
            self.db.delete(station)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise