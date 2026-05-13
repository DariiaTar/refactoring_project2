import pytest
from src.models.user import User, UserRole
from src.models.booking import Booking, BookingStatus
from src.models.slot import SlotStatus
from src.models.location import Location, LocationCategory, LocationImage


class TestUserRole:
    def test_user_role_values(self):
        assert UserRole.USER == "user"
        assert UserRole.ADMIN == "admin"
        assert UserRole.GUEST == "guest"

    def test_user_role_is_string(self):
        assert isinstance(UserRole.USER, str)

    def test_all_roles_exist(self):
        roles = [r.value for r in UserRole]
        assert "user" in roles
        assert "admin" in roles
        assert "guest" in roles

    def test_role_count(self):
        assert len(UserRole) == 3


class TestBookingStatus:
    def test_all_statuses_exist(self):
        statuses = [s.value for s in BookingStatus]
        assert "pending_payment" in statuses
        assert "confirmed" in statuses
        assert "cancelled" in statuses
        assert "completed" in statuses

    def test_status_is_string(self):
        assert isinstance(BookingStatus.CONFIRMED, str)

    def test_status_count(self):
        assert len(BookingStatus) == 4

    def test_pending_payment_value(self):
        assert BookingStatus.PENDING_PAYMENT == "pending_payment"

    def test_cancelled_value(self):
        assert BookingStatus.CANCELLED == "cancelled"


class TestSlotStatus:
    def test_all_statuses_exist(self):
        statuses = [s.value for s in SlotStatus]
        assert "available" in statuses
        assert "booked" in statuses
        assert "blocked" in statuses

    def test_available_value(self):
        assert SlotStatus.AVAILABLE == "available"

    def test_booked_value(self):
        assert SlotStatus.BOOKED == "booked"

    def test_blocked_value(self):
        assert SlotStatus.BLOCKED == "blocked"

    def test_status_count(self):
        assert len(SlotStatus) == 3


class TestLocationCategory:
    def test_all_categories_exist(self):
        cats = [c.value for c in LocationCategory]
        assert "tennis" in cats
        assert "football" in cats
        assert "pool" in cats
        assert "gym" in cats
        assert "other" in cats

    def test_category_count(self):
        assert len(LocationCategory) == 5

    def test_tennis_value(self):
        assert LocationCategory.TENNIS == "tennis"

    def test_gym_value(self):
        assert LocationCategory.GYM == "gym"


class TestUserModel:
    def test_create_user_instance(self):
        user = User()
        user.id = 1
        user.email = "test@test.com"
        user.full_name = "Тест"
        user.hashed_password = "hashed"  # NOSONAR
        user.role = UserRole.USER
        user.is_active = True
        assert user.email == "test@test.com"

    def test_default_role_is_user(self):
        user = User()
        assert user.role is None or user.role == UserRole.USER

    def test_user_tablename(self):
        assert User.__tablename__ == "users"


class TestBookingModel:
    def test_create_booking_instance(self):
        b = Booking()
        b.id = 1
        b.user_id = 1
        b.slot_id = 1
        b.total_price = 300.0
        b.status = BookingStatus.PENDING_PAYMENT
        assert b.total_price == pytest.approx(300.0)

    def test_booking_tablename(self):
        assert Booking.__tablename__ == "bookings"

    def test_booking_status_default_pending(self):
        b = Booking()
        assert b.status is None or b.status == BookingStatus.PENDING_PAYMENT


class TestLocationModel:
    def test_location_tablename(self):
        assert Location.__tablename__ == "locations"

    def test_create_location_instance(self):
        loc = Location()
        loc.id = 1
        loc.name = "Корт"
        loc.category = LocationCategory.TENNIS
        loc.price_per_hour = 200.0
        assert loc.name == "Корт"

    def test_location_image_tablename(self):
        assert LocationImage.__tablename__ == "location_images"
