"""Tests for price calculation logic in BookingService."""
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta

from src.services.booking_service import BookingService
from src.models.slot import Slot, SlotStatus
from src.models.booking import Booking, BookingStatus
from src.models.location import Location
from src.dto.booking_dto import BookingCreateDTO


def make_slot_with_duration(hours: float, minutes: int = 0):
    slot = Slot()
    slot.id = 1
    slot.location_id = 1
    slot.start_time = datetime(2026, 6, 1, 10, 0, 0)
    slot.end_time = datetime(2026, 6, 1, 10, 0, 0) + timedelta(hours=hours, minutes=minutes)
    slot.status = SlotStatus.AVAILABLE
    return slot


def make_location_with_price(price_per_hour: float):
    loc = Location()
    loc.id = 1
    loc.name = "Корт"
    loc.price_per_hour = price_per_hour
    loc.is_active = True
    return loc


def make_booking_with_price(price: float):
    from src.models.user import User
    b = Booking()
    b.id = 1
    b.user_id = 1
    b.slot_id = 1
    b.status = BookingStatus.PENDING_PAYMENT
    b.total_price = price
    b.slot = make_slot_with_duration(2)
    b.user = User()
    b.user.full_name = "Тест"
    b.user.phone = None
    b.notes = None
    b.guest_name = None
    b.guest_email = None
    b.guest_phone = None
    b.created_at = datetime.now(timezone.utc)
    return b


@pytest.fixture
def booking_service():
    db = MagicMock()
    return BookingService(db)


class TestPriceCalculation:
    def test_1_hour_at_300_per_hour(self, booking_service):
        slot = make_slot_with_duration(1)
        loc = make_location_with_price(300.0)
        booking = make_booking_with_price(300.0)

        booking_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        booking_service.location_repo.get_by_id = MagicMock(return_value=loc)
        booking_service.booking_repo.create = MagicMock(return_value=booking)
        booking_service.slot_repo.update_status = MagicMock()

        data = BookingCreateDTO(slot_id=1)
        booking_service.create_booking(1, data)

        call_kwargs = booking_service.booking_repo.create.call_args[1]
        assert call_kwargs["total_price"] == pytest.approx(300.0)

    def test_2_hours_at_300_per_hour(self, booking_service):
        slot = make_slot_with_duration(2)
        loc = make_location_with_price(300.0)
        booking = make_booking_with_price(600.0)

        booking_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        booking_service.location_repo.get_by_id = MagicMock(return_value=loc)
        booking_service.booking_repo.create = MagicMock(return_value=booking)
        booking_service.slot_repo.update_status = MagicMock()

        data = BookingCreateDTO(slot_id=1)
        booking_service.create_booking(1, data)

        call_kwargs = booking_service.booking_repo.create.call_args[1]
        assert call_kwargs["total_price"] == pytest.approx(600.0)

    def test_half_hour_at_200_per_hour(self, booking_service):
        slot = make_slot_with_duration(0, minutes=30)
        loc = make_location_with_price(200.0)
        booking = make_booking_with_price(100.0)

        booking_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        booking_service.location_repo.get_by_id = MagicMock(return_value=loc)
        booking_service.booking_repo.create = MagicMock(return_value=booking)
        booking_service.slot_repo.update_status = MagicMock()

        data = BookingCreateDTO(slot_id=1)
        booking_service.create_booking(1, data)

        call_kwargs = booking_service.booking_repo.create.call_args[1]
        assert call_kwargs["total_price"] == pytest.approx(100.0)

    def test_3_hours_at_500_per_hour(self, booking_service):
        slot = make_slot_with_duration(3)
        loc = make_location_with_price(500.0)
        booking = make_booking_with_price(1500.0)

        booking_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        booking_service.location_repo.get_by_id = MagicMock(return_value=loc)
        booking_service.booking_repo.create = MagicMock(return_value=booking)
        booking_service.slot_repo.update_status = MagicMock()

        data = BookingCreateDTO(slot_id=1)
        booking_service.create_booking(1, data)

        call_kwargs = booking_service.booking_repo.create.call_args[1]
        assert call_kwargs["total_price"] == pytest.approx(1500.0)

    def test_price_passed_to_repo(self, booking_service):
        slot = make_slot_with_duration(2)
        loc = make_location_with_price(400.0)
        booking = make_booking_with_price(800.0)

        booking_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        booking_service.location_repo.get_by_id = MagicMock(return_value=loc)
        booking_service.booking_repo.create = MagicMock(return_value=booking)
        booking_service.slot_repo.update_status = MagicMock()

        data = BookingCreateDTO(slot_id=1)
        booking_service.create_booking(1, data)

        assert booking_service.booking_repo.create.called
        call_kwargs = booking_service.booking_repo.create.call_args[1]
        assert "total_price" in call_kwargs

    def test_price_is_float(self, booking_service):
        slot = make_slot_with_duration(1)
        loc = make_location_with_price(300.0)
        booking = make_booking_with_price(300.0)

        booking_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        booking_service.location_repo.get_by_id = MagicMock(return_value=loc)
        booking_service.booking_repo.create = MagicMock(return_value=booking)
        booking_service.slot_repo.update_status = MagicMock()

        data = BookingCreateDTO(slot_id=1)
        booking_service.create_booking(1, data)

        call_kwargs = booking_service.booking_repo.create.call_args[1]
        assert isinstance(call_kwargs["total_price"], float)

    def test_price_minimum_positive(self, booking_service):
        slot = make_slot_with_duration(1)
        loc = make_location_with_price(1.0)
        booking = make_booking_with_price(1.0)

        booking_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        booking_service.location_repo.get_by_id = MagicMock(return_value=loc)
        booking_service.booking_repo.create = MagicMock(return_value=booking)
        booking_service.slot_repo.update_status = MagicMock()

        data = BookingCreateDTO(slot_id=1)
        booking_service.create_booking(1, data)

        call_kwargs = booking_service.booking_repo.create.call_args[1]
        assert call_kwargs["total_price"] > 0
