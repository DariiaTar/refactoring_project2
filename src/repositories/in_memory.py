from typing import Dict, Optional, List
from datetime import datetime, timezone

from src.models.user import User, UserRole
from src.models.location import Location, LocationCategory
from src.models.slot import Slot, SlotStatus
from src.models.booking import Booking, BookingStatus
from src.repositories.interfaces import (
    IUserRepository, ILocationRepository, ISlotRepository, IBookingRepository
)


class InMemoryUserRepository(IUserRepository):
    def __init__(self):
        self._store: Dict[int, User] = {}
        self._counter = 1

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self._store.get(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self._store.values() if u.email == email), None)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        return list(self._store.values())[skip:skip + limit]

    def create(self, email: str, full_name: str, hashed_password: str, **kwargs) -> User:
        user = User()
        user.id = self._counter
        user.email = email
        user.full_name = full_name
        user.hashed_password = hashed_password
        user.role = kwargs.get("role", UserRole.USER)
        user.phone = kwargs.get("phone")
        user.is_active = True
        self._store[self._counter] = user
        self._counter += 1
        return user

    def update(self, user: User, **kwargs) -> User:
        for key, val in kwargs.items():
            if val is not None:
                setattr(user, key, val)
        return user

    def delete(self, user: User) -> None:
        self._store.pop(user.id, None)


class InMemoryLocationRepository(ILocationRepository):
    def __init__(self):
        self._store: Dict[int, Location] = {}
        self._counter = 1

    def get_by_id(self, location_id: int) -> Optional[Location]:
        return self._store.get(location_id)

    def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Location]:
        items = list(self._store.values())
        if active_only:
            items = [loc for loc in items if loc.is_active]
        return items[skip:skip + limit]

    def create(self, name: str, category: LocationCategory, address: str, price_per_hour: float, **kwargs) -> Location:
        loc = Location()
        loc.id = self._counter
        loc.name = name
        loc.category = category
        loc.address = address
        loc.price_per_hour = price_per_hour
        loc.description = kwargs.get("description")
        loc.capacity = kwargs.get("capacity", 1)
        loc.is_active = kwargs.get("is_active", True)
        loc.created_at = datetime.now(timezone.utc)
        self._store[self._counter] = loc
        self._counter += 1
        return loc

    def update(self, location: Location, **kwargs) -> Location:
        for key, val in kwargs.items():
            if val is not None:
                setattr(location, key, val)
        return location

    def delete(self, location: Location) -> None:
        self._store.pop(location.id, None)


class InMemorySlotRepository(ISlotRepository):
    def __init__(self):
        self._store: Dict[int, Slot] = {}
        self._counter = 1

    def get_by_id(self, slot_id: int) -> Optional[Slot]:
        return self._store.get(slot_id)

    def get_by_location(self, location_id: int, from_date: Optional[datetime] = None) -> List[Slot]:
        slots = [s for s in self._store.values() if s.location_id == location_id]
        if from_date:
            slots = [s for s in slots if s.start_time >= from_date]
        return sorted(slots, key=lambda s: s.start_time)

    def get_available_by_location(self, location_id: int) -> List[Slot]:
        now = datetime.now(timezone.utc)
        return [
            s for s in self._store.values()
            if s.location_id == location_id
            and s.status == SlotStatus.AVAILABLE
            and s.start_time >= now
        ]

    def create(self, location_id: int, start_time: datetime, end_time: datetime) -> Slot:
        slot = Slot()
        slot.id = self._counter
        slot.location_id = location_id
        slot.start_time = start_time
        slot.end_time = end_time
        slot.status = SlotStatus.AVAILABLE
        self._store[self._counter] = slot
        self._counter += 1
        return slot

    def update_status(self, slot: Slot, status: SlotStatus) -> Slot:
        slot.status = status
        return slot

    def delete(self, slot: Slot) -> None:
        self._store.pop(slot.id, None)


class InMemoryBookingRepository(IBookingRepository):
    def __init__(self):
        self._store: Dict[int, Booking] = {}
        self._counter = 1

    def get_by_id(self, booking_id: int) -> Optional[Booking]:
        return self._store.get(booking_id)

    def get_by_user(self, user_id: int) -> List[Booking]:
        return [b for b in self._store.values() if b.user_id == user_id]

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Booking]:
        return list(self._store.values())[skip:skip + limit]

    def create(self, user_id: int, slot_id: int, total_price: float, **kwargs) -> Booking:
        booking = Booking()
        booking.id = self._counter
        booking.user_id = user_id
        booking.slot_id = slot_id
        booking.total_price = total_price
        booking.status = BookingStatus.PENDING_PAYMENT
        booking.notes = kwargs.get("notes")
        booking.guest_name = kwargs.get("guest_name")
        booking.guest_email = kwargs.get("guest_email")
        booking.guest_phone = kwargs.get("guest_phone")
        booking.created_at = datetime.now(timezone.utc)
        self._store[self._counter] = booking
        self._counter += 1
        return booking

    def update_status(self, booking: Booking, status: BookingStatus) -> Booking:
        booking.status = status
        return booking
