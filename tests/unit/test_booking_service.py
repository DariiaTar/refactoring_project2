import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone

from src.services.booking_service import BookingService, SlotService
from src.models.slot import Slot, SlotStatus
from src.models.booking import Booking, BookingStatus
from src.models.location import Location
from src.dto.booking_dto import BookingCreateDTO, SlotCreateDTO


def make_slot(status=SlotStatus.AVAILABLE, location_id=1, hours=2):
    slot = Slot()
    slot.id = 1
    slot.location_id = location_id
    slot.start_time = datetime.now(timezone.utc) + timedelta(hours=1)
    slot.end_time = datetime.now(timezone.utc) + timedelta(hours=1 + hours)
    slot.status = status
    return slot


def make_location(price_per_hour=300.0):
    loc = Location()
    loc.id = 1
    loc.name = "Тенісний корт"
    loc.address = "вул. Спортивна 1"
    loc.price_per_hour = price_per_hour
    loc.is_active = True
    return loc


def make_user():
    from src.models.user import User
    u = User()
    u.id = 1
    u.full_name = "Тест Юзер"
    u.phone = "+380501234567"
    return u


def make_booking(status=BookingStatus.PENDING_PAYMENT, user_id=1, total_price=600.0):
    b = Booking()
    b.id = 1
    b.user_id = user_id
    b.slot_id = 1
    b.status = status
    b.total_price = total_price
    b.slot = make_slot(SlotStatus.BOOKED)
    b.user = make_user()
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


@pytest.fixture
def slot_service():
    db = MagicMock()
    return SlotService(db)


class TestCreateBooking:
    def test_success(self, booking_service):
        slot = make_slot()
        loc = make_location()
        booking = make_booking()

        booking_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        booking_service.location_repo.get_by_id = MagicMock(return_value=loc)
        booking_service.booking_repo.create = MagicMock(return_value=booking)
        booking_service.slot_repo.update_status = MagicMock()

        data = BookingCreateDTO(slot_id=1)
        result = booking_service.create_booking(1, data)
        assert result.total_price == pytest.approx(600.0)

    def test_slot_not_found_raises(self, booking_service):
        booking_service.slot_repo.get_by_id = MagicMock(return_value=None)
        data = BookingCreateDTO(slot_id=999)
        with pytest.raises(HTTPException) as exc:
            booking_service.create_booking(1, data)
        assert exc.value.status_code == 404

    def test_slot_already_booked_raises(self, booking_service):
        slot = make_slot(status=SlotStatus.BOOKED)
        booking_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        data = BookingCreateDTO(slot_id=1)
        with pytest.raises(HTTPException) as exc:
            booking_service.create_booking(1, data)
        assert exc.value.status_code == 400

    def test_slot_blocked_raises(self, booking_service):
        slot = make_slot(status=SlotStatus.BLOCKED)
        booking_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        data = BookingCreateDTO(slot_id=1)
        with pytest.raises(HTTPException) as exc:
            booking_service.create_booking(1, data)
        assert exc.value.status_code == 400

    def test_price_calculated_from_duration(self, booking_service):
        slot = make_slot(hours=3)
        loc = make_location(price_per_hour=200.0)
        booking = make_booking(total_price=600.0)

        booking_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        booking_service.location_repo.get_by_id = MagicMock(return_value=loc)
        booking_service.booking_repo.create = MagicMock(return_value=booking)
        booking_service.slot_repo.update_status = MagicMock()

        data = BookingCreateDTO(slot_id=1)
        booking_service.create_booking(1, data)
        call_kwargs = booking_service.booking_repo.create.call_args[1]
        assert "total_price" in call_kwargs

    def test_slot_status_updated_to_booked(self, booking_service):
        slot = make_slot()
        loc = make_location()
        booking = make_booking()

        booking_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        booking_service.location_repo.get_by_id = MagicMock(return_value=loc)
        booking_service.booking_repo.create = MagicMock(return_value=booking)
        booking_service.slot_repo.update_status = MagicMock()

        data = BookingCreateDTO(slot_id=1)
        booking_service.create_booking(1, data)
        booking_service.slot_repo.update_status.assert_called_once_with(slot, SlotStatus.BOOKED)

    def test_booking_with_guest_info(self, booking_service):
        slot = make_slot()
        loc = make_location()
        booking = make_booking()
        booking.guest_name = "Гість Гостьович"
        booking.guest_email = "guest@test.com"

        booking_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        booking_service.location_repo.get_by_id = MagicMock(return_value=loc)
        booking_service.booking_repo.create = MagicMock(return_value=booking)
        booking_service.slot_repo.update_status = MagicMock()

        data = BookingCreateDTO(slot_id=1, guest_name="Гість Гостьович", guest_email="guest@test.com")
        result = booking_service.create_booking(1, data)
        assert result.guest_name == "Гість Гостьович"

    def test_booking_with_notes(self, booking_service):
        slot = make_slot()
        loc = make_location()
        booking = make_booking()
        booking.notes = "Особливі побажання"

        booking_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        booking_service.location_repo.get_by_id = MagicMock(return_value=loc)
        booking_service.booking_repo.create = MagicMock(return_value=booking)
        booking_service.slot_repo.update_status = MagicMock()

        data = BookingCreateDTO(slot_id=1, notes="Особливі побажання")
        result = booking_service.create_booking(1, data)
        assert result.notes == "Особливі побажання"

    def test_create_booking_returns_dto(self, booking_service):
        slot = make_slot()
        loc = make_location()
        booking = make_booking()

        booking_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        booking_service.location_repo.get_by_id = MagicMock(return_value=loc)
        booking_service.booking_repo.create = MagicMock(return_value=booking)
        booking_service.slot_repo.update_status = MagicMock()

        data = BookingCreateDTO(slot_id=1)
        result = booking_service.create_booking(1, data)
        assert hasattr(result, "id")
        assert hasattr(result, "status")
        assert hasattr(result, "total_price")


class TestCancelBooking:
    def test_cancel_own_booking(self, booking_service):
        booking = make_booking()
        updated = make_booking(status=BookingStatus.CANCELLED)

        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        booking_service.booking_repo.update_status = MagicMock(return_value=updated)
        booking_service.slot_repo.update_status = MagicMock()

        result = booking_service.cancel_booking(1, user_id=1)
        assert result.status == BookingStatus.CANCELLED

    def test_cancel_other_user_booking_raises(self, booking_service):
        booking = make_booking()
        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        with pytest.raises(HTTPException) as exc:
            booking_service.cancel_booking(1, user_id=99, is_admin=False)
        assert exc.value.status_code == 403

    def test_admin_can_cancel_any_booking(self, booking_service):
        booking = make_booking()
        updated = make_booking(status=BookingStatus.CANCELLED)
        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        booking_service.booking_repo.update_status = MagicMock(return_value=updated)
        booking_service.slot_repo.update_status = MagicMock()

        result = booking_service.cancel_booking(1, user_id=99, is_admin=True)
        assert result.status == BookingStatus.CANCELLED

    def test_cancel_already_cancelled_raises(self, booking_service):
        booking = make_booking(status=BookingStatus.CANCELLED)
        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        with pytest.raises(HTTPException) as exc:
            booking_service.cancel_booking(1, user_id=1)
        assert exc.value.status_code == 400

    def test_cancel_nonexistent_booking_raises(self, booking_service):
        booking_service.booking_repo.get_by_id = MagicMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            booking_service.cancel_booking(999, user_id=1)
        assert exc.value.status_code == 404

    def test_cancel_restores_slot_to_available(self, booking_service):
        booking = make_booking()
        updated = make_booking(status=BookingStatus.CANCELLED)
        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        booking_service.booking_repo.update_status = MagicMock(return_value=updated)
        booking_service.slot_repo.update_status = MagicMock()

        booking_service.cancel_booking(1, user_id=1)
        booking_service.slot_repo.update_status.assert_called_once_with(booking.slot, SlotStatus.AVAILABLE)

    def test_cancel_confirmed_booking(self, booking_service):
        booking = make_booking(status=BookingStatus.CONFIRMED)
        updated = make_booking(status=BookingStatus.CANCELLED)
        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        booking_service.booking_repo.update_status = MagicMock(return_value=updated)
        booking_service.slot_repo.update_status = MagicMock()

        result = booking_service.cancel_booking(1, user_id=1)
        assert result.status == BookingStatus.CANCELLED


class TestSlotService:
    def test_delete_booked_slot_raises(self, slot_service):
        slot = make_slot(status=SlotStatus.BOOKED)
        slot_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        with pytest.raises(HTTPException) as exc:
            slot_service.delete(1)
        assert exc.value.status_code == 400

    def test_delete_available_slot_success(self, slot_service):
        slot = make_slot(status=SlotStatus.AVAILABLE)
        slot_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        slot_service.slot_repo.delete = MagicMock()
        slot_service.location_repo.get_by_id = MagicMock(return_value=make_location())
        slot_service.delete(1)
        slot_service.slot_repo.delete.assert_called_once()

    def test_delete_nonexistent_slot_raises(self, slot_service):
        slot_service.slot_repo.get_by_id = MagicMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            slot_service.delete(999)
        assert exc.value.status_code == 404

    def test_delete_blocked_slot_success(self, slot_service):
        slot = make_slot(status=SlotStatus.BLOCKED)
        slot_service.slot_repo.get_by_id = MagicMock(return_value=slot)
        slot_service.slot_repo.delete = MagicMock()
        slot_service.delete(1)
        slot_service.slot_repo.delete.assert_called_once()

    def test_create_slot_location_not_found_raises(self, slot_service):
        slot_service.location_repo.get_by_id = MagicMock(return_value=None)
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=2)
        data = SlotCreateDTO(location_id=999, start_time=start, end_time=end)
        with pytest.raises(HTTPException) as exc:
            slot_service.create(data)
        assert exc.value.status_code == 404

    def test_create_slot_success(self, slot_service):
        loc = make_location()
        slot = make_slot()
        slot_service.location_repo.get_by_id = MagicMock(return_value=loc)
        slot_service.slot_repo.create = MagicMock(return_value=slot)

        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=2)
        data = SlotCreateDTO(location_id=1, start_time=start, end_time=end)
        result = slot_service.create(data)
        assert result.id == 1

    def test_get_by_location_returns_list(self, slot_service):
        slots = [make_slot(), make_slot()]
        slots[1].id = 2
        slot_service.slot_repo.get_by_location = MagicMock(return_value=slots)
        result = slot_service.get_by_location(1)
        assert len(result) == 2

    def test_get_available_returns_only_available(self, slot_service):
        slot = make_slot(status=SlotStatus.AVAILABLE)
        slot_service.slot_repo.get_available_by_location = MagicMock(return_value=[slot])
        result = slot_service.get_available(1)
        assert all(s.status == SlotStatus.AVAILABLE for s in result)

    def test_get_available_empty_list(self, slot_service):
        slot_service.slot_repo.get_available_by_location = MagicMock(return_value=[])
        result = slot_service.get_available(1)
        assert result == []


class TestPayBooking:
    def test_pay_pending_booking_succeeds(self, booking_service):
        booking = make_booking()
        location = make_location()
        confirmed = make_booking(status=BookingStatus.CONFIRMED)

        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        booking_service.booking_repo.update_status = MagicMock(return_value=confirmed)
        booking_service.location_repo.get_by_id = MagicMock(return_value=location)

        result = booking_service.pay_booking(1, user_id=1)
        assert result.status == BookingStatus.CONFIRMED

    def test_pay_booking_not_found_raises(self, booking_service):
        booking_service.booking_repo.get_by_id = MagicMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            booking_service.pay_booking(999, user_id=1)
        assert exc.value.status_code == 404

    def test_pay_other_user_booking_raises(self, booking_service):
        booking = make_booking()
        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        with pytest.raises(HTTPException) as exc:
            booking_service.pay_booking(1, user_id=99, is_admin=False)
        assert exc.value.status_code == 403

    def test_pay_already_confirmed_raises(self, booking_service):
        booking = make_booking(status=BookingStatus.CONFIRMED)
        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        with pytest.raises(HTTPException) as exc:
            booking_service.pay_booking(1, user_id=1)
        assert exc.value.status_code == 400

    def test_admin_can_pay_any_booking(self, booking_service):
        booking = make_booking()
        location = make_location()
        confirmed = make_booking(status=BookingStatus.CONFIRMED)

        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        booking_service.booking_repo.update_status = MagicMock(return_value=confirmed)
        booking_service.location_repo.get_by_id = MagicMock(return_value=location)

        result = booking_service.pay_booking(1, user_id=99, is_admin=True)
        assert result.status == BookingStatus.CONFIRMED

    def test_pay_cancelled_booking_raises(self, booking_service):
        booking = make_booking(status=BookingStatus.CANCELLED)
        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        with pytest.raises(HTTPException) as exc:
            booking_service.pay_booking(1, user_id=1)
        assert exc.value.status_code == 400

    def test_pay_returns_details_dto(self, booking_service):
        booking = make_booking()
        location = make_location()
        confirmed = make_booking(status=BookingStatus.CONFIRMED)

        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        booking_service.booking_repo.update_status = MagicMock(return_value=confirmed)
        booking_service.location_repo.get_by_id = MagicMock(return_value=location)

        result = booking_service.pay_booking(1, user_id=1)
        assert hasattr(result, "location_name")
        assert hasattr(result, "user_full_name")


class TestGetBooking:
    def test_user_can_get_own_booking(self, booking_service):
        booking = make_booking()
        location = make_location()
        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        booking_service.location_repo.get_by_id = MagicMock(return_value=location)

        result = booking_service.get_booking(1, user_id=1)
        assert result.id == 1

    def test_user_cannot_get_other_booking(self, booking_service):
        booking = make_booking()
        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        with pytest.raises(HTTPException) as exc:
            booking_service.get_booking(1, user_id=99, is_admin=False)
        assert exc.value.status_code == 403

    def test_admin_can_get_any_booking(self, booking_service):
        booking = make_booking()
        location = make_location()
        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        booking_service.location_repo.get_by_id = MagicMock(return_value=location)

        result = booking_service.get_booking(1, user_id=99, is_admin=True)
        assert result.id == 1

    def test_get_nonexistent_booking_raises(self, booking_service):
        booking_service.booking_repo.get_by_id = MagicMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            booking_service.get_booking(999, user_id=1)
        assert exc.value.status_code == 404

    def test_get_booking_returns_location_info(self, booking_service):
        booking = make_booking()
        location = make_location()
        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        booking_service.location_repo.get_by_id = MagicMock(return_value=location)

        result = booking_service.get_booking(1, user_id=1)
        assert result.location_name == "Тенісний корт"

    def test_get_booking_returns_user_info(self, booking_service):
        booking = make_booking()
        location = make_location()
        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        booking_service.location_repo.get_by_id = MagicMock(return_value=location)

        result = booking_service.get_booking(1, user_id=1)
        assert result.user_full_name == "Тест Юзер"


class TestUpdateStatus:
    def test_update_to_completed(self, booking_service):
        booking = make_booking(status=BookingStatus.CONFIRMED)
        completed = make_booking(status=BookingStatus.COMPLETED)

        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        booking_service.booking_repo.update_status = MagicMock(return_value=completed)

        result = booking_service.update_status(1, BookingStatus.COMPLETED)
        assert result.status == BookingStatus.COMPLETED

    def test_update_nonexistent_booking_raises(self, booking_service):
        booking_service.booking_repo.get_by_id = MagicMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            booking_service.update_status(999, BookingStatus.COMPLETED)
        assert exc.value.status_code == 404

    def test_update_status_calls_repo(self, booking_service):
        booking = make_booking()
        updated = make_booking(status=BookingStatus.CONFIRMED)
        booking_service.booking_repo.get_by_id = MagicMock(return_value=booking)
        booking_service.booking_repo.update_status = MagicMock(return_value=updated)

        booking_service.update_status(1, BookingStatus.CONFIRMED)
        booking_service.booking_repo.update_status.assert_called_once_with(booking, BookingStatus.CONFIRMED)


class TestGetAllBookings:
    def test_get_all_returns_list(self, booking_service):
        bookings = [make_booking(), make_booking()]
        bookings[1].id = 2
        booking_service.booking_repo.get_all = MagicMock(return_value=bookings)
        result = booking_service.get_all_bookings()
        assert len(result) == 2

    def test_get_all_empty(self, booking_service):
        booking_service.booking_repo.get_all = MagicMock(return_value=[])
        result = booking_service.get_all_bookings()
        assert result == []

    def test_get_user_bookings(self, booking_service):
        bookings = [make_booking()]
        booking_service.booking_repo.get_by_user = MagicMock(return_value=bookings)
        result = booking_service.get_user_bookings(1)
        assert len(result) == 1

    def test_get_user_bookings_empty(self, booking_service):
        booking_service.booking_repo.get_by_user = MagicMock(return_value=[])
        result = booking_service.get_user_bookings(99)
        assert result == []
