from sqlalchemy.orm import Session
from typing import Optional, List
from src.models.booking import Booking, BookingStatus


class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, booking_id: int) -> Optional[Booking]:
        return self.db.query(Booking).filter(Booking.id == booking_id).first()

    def get_by_user(self, user_id: int) -> List[Booking]:
        return self.db.query(Booking).filter(Booking.user_id == user_id).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Booking]:
        return self.db.query(Booking).offset(skip).limit(limit).all()

    def create(self, user_id: int, slot_id: int, total_price: float, **kwargs) -> Booking:
        booking = Booking(user_id=user_id, slot_id=slot_id, total_price=total_price, **kwargs)
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def update_status(self, booking: Booking, status: BookingStatus) -> Booking:
        booking.status = status
        self.db.commit()
        self.db.refresh(booking)
        return booking
