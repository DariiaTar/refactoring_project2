"""Tests for In-Memory repository implementations."""
import pytest
from datetime import datetime, timezone, timedelta

from src.repositories.in_memory import (
    InMemoryUserRepository,
    InMemoryLocationRepository,
    InMemorySlotRepository,
    InMemoryBookingRepository,
)
from src.repositories.interfaces import (
    IUserRepository, ILocationRepository, ISlotRepository, IBookingRepository
)
from src.models.user import UserRole
from src.models.location import LocationCategory
from src.models.slot import SlotStatus
from src.models.booking import BookingStatus


# ── InMemoryUserRepository ────────────────────────────────────────────────

class TestInMemoryUserRepository:
    def setup_method(self):
        self.repo = InMemoryUserRepository()

    def test_implements_interface(self):
        assert isinstance(self.repo, IUserRepository)

    def test_create_assigns_id(self):
        user = self.repo.create("a@b.com", "Alice", "hash")
        assert user.id == 1

    def test_create_increments_id(self):
        u1 = self.repo.create("a@b.com", "Alice", "hash")
        u2 = self.repo.create("b@b.com", "Bob", "hash")
        assert u2.id == u1.id + 1

    def test_create_stores_email(self):
        user = self.repo.create("alice@x.com", "Alice", "hash")
        assert user.email == "alice@x.com"

    def test_create_stores_full_name(self):
        user = self.repo.create("a@b.com", "Alice Alicevych", "hash")
        assert user.full_name == "Alice Alicevych"

    def test_create_default_role_is_user(self):
        user = self.repo.create("a@b.com", "Alice", "hash")
        assert user.role == UserRole.USER

    def test_create_custom_role(self):
        user = self.repo.create("a@b.com", "Alice", "hash", role=UserRole.ADMIN)
        assert user.role == UserRole.ADMIN

    def test_create_is_active_true(self):
        user = self.repo.create("a@b.com", "Alice", "hash")
        assert user.is_active is True

    def test_get_by_id_returns_user(self):
        created = self.repo.create("a@b.com", "Alice", "hash")
        found = self.repo.get_by_id(created.id)
        assert found is created

    def test_get_by_id_returns_none_for_missing(self):
        assert self.repo.get_by_id(999) is None

    def test_get_by_email_returns_user(self):
        created = self.repo.create("alice@x.com", "Alice", "hash")
        found = self.repo.get_by_email("alice@x.com")
        assert found is created

    def test_get_by_email_returns_none_for_missing(self):
        assert self.repo.get_by_email("nobody@x.com") is None

    def test_get_all_returns_all(self):
        self.repo.create("a@b.com", "A", "hash")
        self.repo.create("b@b.com", "B", "hash")
        assert len(self.repo.get_all()) == 2

    def test_get_all_skip(self):
        for i in range(5):
            self.repo.create(f"u{i}@b.com", f"User{i}", "hash")
        result = self.repo.get_all(skip=3)
        assert len(result) == 2

    def test_get_all_limit(self):
        for i in range(5):
            self.repo.create(f"u{i}@b.com", f"User{i}", "hash")
        result = self.repo.get_all(limit=2)
        assert len(result) == 2

    def test_update_sets_attribute(self):
        user = self.repo.create("a@b.com", "Alice", "hash")
        self.repo.update(user, full_name="Alice Updated")
        assert user.full_name == "Alice Updated"

    def test_update_ignores_none(self):
        user = self.repo.create("a@b.com", "Alice", "hash")
        self.repo.update(user, full_name=None)
        assert user.full_name == "Alice"

    def test_delete_removes_user(self):
        user = self.repo.create("a@b.com", "Alice", "hash")
        self.repo.delete(user)
        assert self.repo.get_by_id(user.id) is None

    def test_delete_nonexistent_no_error(self):
        from src.models.user import User
        ghost = User()
        ghost.id = 999
        self.repo.delete(ghost)


# ── InMemoryLocationRepository ────────────────────────────────────────────

class TestInMemoryLocationRepository:
    def setup_method(self):
        self.repo = InMemoryLocationRepository()

    def test_implements_interface(self):
        assert isinstance(self.repo, ILocationRepository)

    def test_create_assigns_id(self):
        loc = self.repo.create("Court 1", LocationCategory.TENNIS, "vul. 1", 300.0)
        assert loc.id == 1

    def test_create_stores_name(self):
        loc = self.repo.create("Pool", LocationCategory.POOL, "vul. 2", 200.0)
        assert loc.name == "Pool"

    def test_create_stores_price(self):
        loc = self.repo.create("Gym", LocationCategory.GYM, "vul. 3", 150.0)
        assert loc.price_per_hour == pytest.approx(150.0)

    def test_create_is_active_default_true(self):
        loc = self.repo.create("Gym", LocationCategory.GYM, "vul. 3", 150.0)
        assert loc.is_active is True

    def test_get_by_id_found(self):
        loc = self.repo.create("Court", LocationCategory.TENNIS, "vul.", 300.0)
        assert self.repo.get_by_id(loc.id) is loc

    def test_get_by_id_not_found(self):
        assert self.repo.get_by_id(999) is None

    def test_get_all_returns_all(self):
        self.repo.create("A", LocationCategory.TENNIS, "a", 100.0)
        self.repo.create("B", LocationCategory.GYM, "b", 200.0)
        assert len(self.repo.get_all()) == 2

    def test_get_all_active_only(self):
        loc1 = self.repo.create("A", LocationCategory.TENNIS, "a", 100.0)
        loc2 = self.repo.create("B", LocationCategory.GYM, "b", 200.0)
        self.repo.update(loc2, is_active=False)
        result = self.repo.get_all(active_only=True)
        assert len(result) == 1
        assert result[0] is loc1

    def test_update_name(self):
        loc = self.repo.create("Old", LocationCategory.TENNIS, "a", 100.0)
        self.repo.update(loc, name="New")
        assert loc.name == "New"

    def test_delete_removes(self):
        loc = self.repo.create("X", LocationCategory.GYM, "x", 100.0)
        self.repo.delete(loc)
        assert self.repo.get_by_id(loc.id) is None


# ── InMemorySlotRepository ────────────────────────────────────────────────

class TestInMemorySlotRepository:
    def setup_method(self):
        self.repo = InMemorySlotRepository()
        self.future = datetime.now(timezone.utc) + timedelta(hours=2)

    def test_implements_interface(self):
        assert isinstance(self.repo, ISlotRepository)

    def test_create_assigns_id(self):
        slot = self.repo.create(1, self.future, self.future + timedelta(hours=1))
        assert slot.id == 1

    def test_create_status_available(self):
        slot = self.repo.create(1, self.future, self.future + timedelta(hours=1))
        assert slot.status == SlotStatus.AVAILABLE

    def test_get_by_id_found(self):
        slot = self.repo.create(1, self.future, self.future + timedelta(hours=1))
        assert self.repo.get_by_id(slot.id) is slot

    def test_get_by_id_not_found(self):
        assert self.repo.get_by_id(999) is None

    def test_get_by_location_filters_correctly(self):
        self.repo.create(1, self.future, self.future + timedelta(hours=1))
        self.repo.create(1, self.future + timedelta(hours=2), self.future + timedelta(hours=3))
        self.repo.create(2, self.future, self.future + timedelta(hours=1))
        result = self.repo.get_by_location(1)
        assert len(result) == 2

    def test_get_by_location_sorted_by_start(self):
        s2 = self.future + timedelta(hours=3)
        s1 = self.future + timedelta(hours=1)
        self.repo.create(1, s2, s2 + timedelta(hours=1))
        self.repo.create(1, s1, s1 + timedelta(hours=1))
        result = self.repo.get_by_location(1)
        assert result[0].start_time < result[1].start_time

    def test_get_by_location_with_from_date_filter(self):
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=5)
        self.repo.create(1, past, past + timedelta(hours=1))
        self.repo.create(1, self.future, self.future + timedelta(hours=1))
        result = self.repo.get_by_location(1, from_date=now)
        assert len(result) == 1

    def test_get_available_by_location(self):
        slot = self.repo.create(1, self.future, self.future + timedelta(hours=1))
        result = self.repo.get_available_by_location(1)
        assert slot in result

    def test_get_available_excludes_booked(self):
        slot = self.repo.create(1, self.future, self.future + timedelta(hours=1))
        self.repo.update_status(slot, SlotStatus.BOOKED)
        assert self.repo.get_available_by_location(1) == []

    def test_update_status_changes_status(self):
        slot = self.repo.create(1, self.future, self.future + timedelta(hours=1))
        self.repo.update_status(slot, SlotStatus.BOOKED)
        assert slot.status == SlotStatus.BOOKED

    def test_delete_removes_slot(self):
        slot = self.repo.create(1, self.future, self.future + timedelta(hours=1))
        self.repo.delete(slot)
        assert self.repo.get_by_id(slot.id) is None


# ── InMemoryBookingRepository ─────────────────────────────────────────────

class TestInMemoryBookingRepository:
    def setup_method(self):
        self.repo = InMemoryBookingRepository()

    def test_implements_interface(self):
        assert isinstance(self.repo, IBookingRepository)

    def test_create_assigns_id(self):
        b = self.repo.create(1, 1, 300.0)
        assert b.id == 1

    def test_create_status_pending_payment(self):
        b = self.repo.create(1, 1, 300.0)
        assert b.status == BookingStatus.PENDING_PAYMENT

    def test_create_stores_price(self):
        b = self.repo.create(1, 1, 450.0)
        assert b.total_price == pytest.approx(450.0)

    def test_create_stores_notes(self):
        b = self.repo.create(1, 1, 300.0, notes="Прошу не спізнюватись")
        assert b.notes == "Прошу не спізнюватись"

    def test_create_guest_fields(self):
        b = self.repo.create(1, 1, 300.0, guest_name="Іван", guest_email="i@x.com", guest_phone="+38050")
        assert b.guest_name == "Іван"
        assert b.guest_email == "i@x.com"
        assert b.guest_phone == "+38050"

    def test_get_by_id_found(self):
        b = self.repo.create(1, 1, 300.0)
        assert self.repo.get_by_id(b.id) is b

    def test_get_by_id_not_found(self):
        assert self.repo.get_by_id(999) is None

    def test_get_by_user_returns_user_bookings(self):
        self.repo.create(1, 1, 300.0)
        self.repo.create(1, 2, 200.0)
        self.repo.create(2, 3, 100.0)
        result = self.repo.get_by_user(1)
        assert len(result) == 2

    def test_get_by_user_returns_empty_list(self):
        assert self.repo.get_by_user(99) == []

    def test_get_all_returns_all(self):
        self.repo.create(1, 1, 100.0)
        self.repo.create(2, 2, 200.0)
        assert len(self.repo.get_all()) == 2

    def test_get_all_skip_limit(self):
        for i in range(5):
            self.repo.create(i + 1, i + 1, 100.0)
        result = self.repo.get_all(skip=2, limit=2)
        assert len(result) == 2

    def test_update_status_changes_status(self):
        b = self.repo.create(1, 1, 300.0)
        self.repo.update_status(b, BookingStatus.CONFIRMED)
        assert b.status == BookingStatus.CONFIRMED

    def test_update_status_to_cancelled(self):
        b = self.repo.create(1, 1, 300.0)
        self.repo.update_status(b, BookingStatus.CANCELLED)
        assert b.status == BookingStatus.CANCELLED

    def test_id_increments(self):
        b1 = self.repo.create(1, 1, 100.0)
        b2 = self.repo.create(1, 2, 200.0)
        assert b2.id == b1.id + 1
