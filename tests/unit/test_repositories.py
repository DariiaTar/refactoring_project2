from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta

from src.repositories.user_repository import UserRepository
from src.repositories.location_repository import LocationRepository
from src.repositories.booking_repository import BookingRepository
from src.repositories.slot_repository import SlotRepository
from src.models.user import User
from src.models.location import Location, LocationCategory, LocationImage
from src.models.booking import Booking, BookingStatus
from src.models.slot import Slot, SlotStatus


def make_db():
    db = MagicMock()
    query_mock = MagicMock()
    db.query.return_value = query_mock
    query_mock.filter.return_value = query_mock
    query_mock.offset.return_value = query_mock
    query_mock.limit.return_value = query_mock
    query_mock.order_by.return_value = query_mock
    query_mock.update.return_value = None
    return db, query_mock


class TestUserRepository:
    def test_get_by_id_calls_query(self):
        db, q = make_db()
        q.first.return_value = None
        repo = UserRepository(db)
        repo.get_by_id(1)
        db.query.assert_called_once_with(User)

    def test_get_by_id_returns_user(self):
        db, q = make_db()
        user = User()
        user.id = 1
        q.first.return_value = user
        repo = UserRepository(db)
        result = repo.get_by_id(1)
        assert result == user

    def test_get_by_id_returns_none_when_missing(self):
        db, q = make_db()
        q.first.return_value = None
        repo = UserRepository(db)
        result = repo.get_by_id(999)
        assert result is None

    def test_get_by_email_calls_query(self):
        db, q = make_db()
        q.first.return_value = None
        repo = UserRepository(db)
        repo.get_by_email("test@example.com")
        db.query.assert_called_once_with(User)

    def test_get_by_email_returns_user(self):
        db, q = make_db()
        user = User()
        user.email = "found@example.com"
        q.first.return_value = user
        repo = UserRepository(db)
        result = repo.get_by_email("found@example.com")
        assert result == user

    def test_get_all_calls_offset_limit(self):
        db, q = make_db()
        q.all.return_value = []
        repo = UserRepository(db)
        repo.get_all(skip=10, limit=20)
        q.offset.assert_called_once_with(10)
        q.limit.assert_called_once_with(20)

    def test_create_adds_and_commits(self):
        db = MagicMock()
        repo = UserRepository(db)
        repo.create(
            email="new@example.com",
            full_name="Новий Юзер",
            hashed_password="hashed",  # NOSONAR
        )
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    def test_create_returns_user(self):
        db = MagicMock()
        repo = UserRepository(db)
        result = repo.create(
            email="new@example.com",
            full_name="Новий",
            hashed_password="hashed",  # NOSONAR
        )
        assert result is not None

    def test_update_sets_attributes(self):
        db = MagicMock()
        user = User()
        user.full_name = "Старе ім'я"
        repo = UserRepository(db)
        repo.update(user, full_name="Нове ім'я")
        assert user.full_name == "Нове ім'я"
        db.commit.assert_called_once()

    def test_update_ignores_none_values(self):
        db = MagicMock()
        user = User()
        user.phone = "+380501111111"
        repo = UserRepository(db)
        repo.update(user, phone=None)
        assert user.phone == "+380501111111"

    def test_delete_calls_db_delete(self):
        db = MagicMock()
        user = User()
        repo = UserRepository(db)
        repo.delete(user)
        db.delete.assert_called_once_with(user)
        db.commit.assert_called_once()


class TestLocationRepository:
    def test_get_by_id_returns_location(self):
        db, q = make_db()
        loc = Location()
        q.first.return_value = loc
        repo = LocationRepository(db)
        result = repo.get_by_id(1)
        assert result == loc

    def test_get_by_id_returns_none(self):
        db, q = make_db()
        q.first.return_value = None
        repo = LocationRepository(db)
        result = repo.get_by_id(999)
        assert result is None

    def test_get_all_applies_active_filter(self):
        db, q = make_db()
        q.all.return_value = []
        repo = LocationRepository(db)
        repo.get_all(active_only=True)
        q.filter.assert_called()

    def test_get_all_returns_list(self):
        db, q = make_db()
        locs = [Location(), Location()]
        q.all.return_value = locs
        repo = LocationRepository(db)
        result = repo.get_all()
        assert len(result) == 2

    def test_create_commits_and_refreshes(self):
        db = MagicMock()
        repo = LocationRepository(db)
        repo.create(
            name="Корт",
            category=LocationCategory.TENNIS,
            address="вул. 1",
            price_per_hour=200.0,
        )
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    def test_update_sets_attributes(self):
        db = MagicMock()
        loc = Location()
        loc.name = "Старий корт"
        repo = LocationRepository(db)
        repo.update(loc, name="Новий корт")
        assert loc.name == "Новий корт"

    def test_delete_removes_location(self):
        db = MagicMock()
        loc = Location()
        repo = LocationRepository(db)
        repo.delete(loc)
        db.delete.assert_called_once_with(loc)
        db.commit.assert_called_once()

    def test_add_image_creates_image(self):
        db = MagicMock()
        q = MagicMock()
        db.query.return_value = q
        q.filter.return_value = q
        repo = LocationRepository(db)
        repo.add_image(1, "/uploads/img.jpg", is_primary=False)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_add_primary_image_clears_others(self):
        db = MagicMock()
        q = MagicMock()
        db.query.return_value = q
        q.filter.return_value = q
        repo = LocationRepository(db)
        repo.add_image(1, "/uploads/primary.jpg", is_primary=True)
        q.update.assert_called_once_with({"is_primary": False})

    def test_delete_image_removes_if_exists(self):
        db, q = make_db()
        img = LocationImage()
        q.first.return_value = img
        repo = LocationRepository(db)
        repo.delete_image(1)
        db.delete.assert_called_once_with(img)

    def test_delete_image_does_nothing_if_not_found(self):
        db, q = make_db()
        q.first.return_value = None
        repo = LocationRepository(db)
        repo.delete_image(999)
        db.delete.assert_not_called()


class TestSlotRepository:
    def test_get_by_id_returns_slot(self):
        db, q = make_db()
        slot = Slot()
        q.first.return_value = slot
        repo = SlotRepository(db)
        result = repo.get_by_id(1)
        assert result == slot

    def test_get_by_id_returns_none(self):
        db, q = make_db()
        q.first.return_value = None
        repo = SlotRepository(db)
        assert repo.get_by_id(999) is None

    def test_get_by_location_returns_list(self):
        db, q = make_db()
        slots = [Slot(), Slot()]
        q.all.return_value = slots
        repo = SlotRepository(db)
        result = repo.get_by_location(1)
        assert len(result) == 2

    def test_create_slot_commits(self):
        db = MagicMock()
        repo = SlotRepository(db)
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=2)
        repo.create(1, start, end)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_update_status_commits(self):
        db = MagicMock()
        slot = Slot()
        slot.status = SlotStatus.AVAILABLE
        repo = SlotRepository(db)
        repo.update_status(slot, SlotStatus.BOOKED)
        assert slot.status == SlotStatus.BOOKED
        db.commit.assert_called_once()

    def test_delete_slot(self):
        db = MagicMock()
        slot = Slot()
        repo = SlotRepository(db)
        repo.delete(slot)
        db.delete.assert_called_once_with(slot)


class TestBookingRepository:
    def test_get_by_id_returns_booking(self):
        db, q = make_db()
        booking = Booking()
        q.first.return_value = booking
        repo = BookingRepository(db)
        result = repo.get_by_id(1)
        assert result == booking

    def test_get_by_id_returns_none(self):
        db, q = make_db()
        q.first.return_value = None
        repo = BookingRepository(db)
        assert repo.get_by_id(999) is None

    def test_get_by_user_returns_list(self):
        db, q = make_db()
        bookings = [Booking(), Booking()]
        q.all.return_value = bookings
        repo = BookingRepository(db)
        result = repo.get_by_user(1)
        assert len(result) == 2

    def test_get_all_uses_offset_limit(self):
        db, q = make_db()
        q.all.return_value = []
        repo = BookingRepository(db)
        repo.get_all(skip=5, limit=10)
        q.offset.assert_called_once_with(5)
        q.limit.assert_called_once_with(10)

    def test_create_booking_commits(self):
        db = MagicMock()
        repo = BookingRepository(db)
        repo.create(user_id=1, slot_id=1, total_price=300.0)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_update_status_changes_status(self):
        db = MagicMock()
        booking = Booking()
        booking.status = BookingStatus.PENDING_PAYMENT
        repo = BookingRepository(db)
        repo.update_status(booking, BookingStatus.CONFIRMED)
        assert booking.status == BookingStatus.CONFIRMED
        db.commit.assert_called_once()
