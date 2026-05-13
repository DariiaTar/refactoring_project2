from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timezone
from src.models.slot import Slot, SlotStatus


class SlotRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, slot_id: int) -> Optional[Slot]:
        return self.db.query(Slot).filter(Slot.id == slot_id).first()

    def get_by_location(self, location_id: int, from_date: Optional[datetime] = None) -> List[Slot]:
        query = self.db.query(Slot).filter(Slot.location_id == location_id)
        if from_date:
            query = query.filter(Slot.start_time >= from_date)
        return query.order_by(Slot.start_time).all()

    def get_available_by_location(self, location_id: int) -> List[Slot]:
        return self.db.query(Slot).filter(
            Slot.location_id == location_id,
            Slot.status == SlotStatus.AVAILABLE,
            Slot.start_time >= datetime.now(timezone.utc)
        ).order_by(Slot.start_time).all()

    def create(self, location_id: int, start_time: datetime, end_time: datetime) -> Slot:
        slot = Slot(location_id=location_id, start_time=start_time, end_time=end_time)
        self.db.add(slot)
        self.db.commit()
        self.db.refresh(slot)
        return slot

    def update_status(self, slot: Slot, status: SlotStatus) -> Slot:
        slot.status = status
        self.db.commit()
        self.db.refresh(slot)
        return slot

    def delete(self, slot: Slot) -> None:
        self.db.delete(slot)
        self.db.commit()
