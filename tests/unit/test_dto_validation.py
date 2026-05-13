import pytest
from pydantic import ValidationError
from datetime import datetime, timedelta, timezone

from src.dto.user_dto import UserRegisterDTO, UserLoginDTO, UserUpdateDTO
from src.dto.location_dto import LocationCreateDTO, LocationUpdateDTO
from src.dto.booking_dto import SlotCreateDTO, BookingCreateDTO, BookingStatusUpdateDTO
from src.models.location import LocationCategory
from src.models.booking import BookingStatus


class TestUserRegisterDTO:
    def test_valid_data(self):
        dto = UserRegisterDTO(email="test@test.com", full_name="Іван Тест", password="pass123")  # NOSONAR
        assert dto.email == "test@test.com"

    def test_short_password_raises(self):
        with pytest.raises(ValidationError):
            UserRegisterDTO(email="test@test.com", full_name="Тест", password="123")  # NOSONAR

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            UserRegisterDTO(email="not-an-email", full_name="Тест", password="pass123")  # NOSONAR

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            UserRegisterDTO(email="test@test.com", full_name="   ", password="pass123")  # NOSONAR

    def test_password_exactly_6_chars_ok(self):
        dto = UserRegisterDTO(email="a@b.com", full_name="Тест", password="123456")  # NOSONAR
        assert dto.password == "123456"

    def test_password_5_chars_raises(self):
        with pytest.raises(ValidationError):
            UserRegisterDTO(email="a@b.com", full_name="Тест", password="12345")  # NOSONAR

    def test_valid_phone(self):
        dto = UserRegisterDTO(email="a@b.com", full_name="Тест", password="pass123", phone="+380501234567")  # NOSONAR
        assert dto.phone == "+380501234567"

    def test_invalid_phone_raises(self):
        with pytest.raises(ValidationError):
            UserRegisterDTO(email="a@b.com", full_name="Тест", password="pass123", phone="abc")  # NOSONAR

    def test_phone_none_allowed(self):
        dto = UserRegisterDTO(email="a@b.com", full_name="Тест", password="pass123", phone=None)  # NOSONAR
        assert dto.phone is None

    def test_missing_email_raises(self):
        with pytest.raises(ValidationError):
            UserRegisterDTO(full_name="Тест", password="pass123")  # NOSONAR

    def test_missing_password_raises(self):
        with pytest.raises(ValidationError):
            UserRegisterDTO(email="a@b.com", full_name="Тест")

    def test_long_password_ok(self):
        dto = UserRegisterDTO(email="a@b.com", full_name="Тест", password="a" * 50)  # NOSONAR
        assert len(dto.password) == 50

    def test_special_chars_in_name_ok(self):
        dto = UserRegisterDTO(email="a@b.com", full_name="Іван-Петро О'Брайен", password="pass123")  # NOSONAR
        assert dto.full_name == "Іван-Петро О'Брайен"

    def test_email_is_valid_string(self):
        dto = UserRegisterDTO(email="User@Example.Com", full_name="Тест", password="pass123")  # NOSONAR
        assert "@" in dto.email


class TestUserLoginDTO:
    def test_valid_login(self):
        dto = UserLoginDTO(email="user@test.com", password="pass123")  # NOSONAR
        assert dto.email == "user@test.com"

    def test_missing_email_raises(self):
        with pytest.raises(ValidationError):
            UserLoginDTO(password="pass123")  # NOSONAR

    def test_missing_password_raises(self):
        with pytest.raises(ValidationError):
            UserLoginDTO(email="user@test.com")

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            UserLoginDTO(email="notvalid", password="pass123")  # NOSONAR


class TestUserUpdateDTO:
    def test_all_none_allowed(self):
        dto = UserUpdateDTO()
        assert dto.full_name is None
        assert dto.phone is None

    def test_update_name_only(self):
        dto = UserUpdateDTO(full_name="Нове Ім'я")
        assert dto.full_name == "Нове Ім'я"

    def test_update_phone_only(self):
        dto = UserUpdateDTO(phone="+380671234567")
        assert dto.phone == "+380671234567"


class TestLocationCreateDTO:
    def test_valid_data(self):
        dto = LocationCreateDTO(
            name="Корт",
            category=LocationCategory.TENNIS,
            address="вул. Тестова 1",
            price_per_hour=200.0,
        )
        assert dto.price_per_hour == pytest.approx(200.0)

    def test_negative_price_raises(self):
        with pytest.raises(ValidationError):
            LocationCreateDTO(
                name="Корт",
                category=LocationCategory.TENNIS,
                address="вул. Тестова 1",
                price_per_hour=-100.0,
            )

    def test_zero_price_raises(self):
        with pytest.raises(ValidationError):
            LocationCreateDTO(
                name="Корт",
                category=LocationCategory.TENNIS,
                address="вул. Тестова 1",
                price_per_hour=0,
            )

    def test_zero_capacity_raises(self):
        with pytest.raises(ValidationError):
            LocationCreateDTO(
                name="Корт",
                category=LocationCategory.TENNIS,
                address="вул. Тестова 1",
                price_per_hour=100.0,
                capacity=0,
            )

    def test_negative_capacity_raises(self):
        with pytest.raises(ValidationError):
            LocationCreateDTO(
                name="Корт",
                category=LocationCategory.TENNIS,
                address="вул. Тестова 1",
                price_per_hour=100.0,
                capacity=-5,
            )

    def test_all_categories_valid(self):
        for cat in LocationCategory:
            dto = LocationCreateDTO(
                name="Локація",
                category=cat,
                address="вул. 1",
                price_per_hour=100.0,
            )
            assert dto.category == cat

    def test_invalid_category_raises(self):
        with pytest.raises(ValidationError):
            LocationCreateDTO(
                name="Корт",
                category="invalid_category",
                address="вул. 1",
                price_per_hour=100.0,
            )

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            LocationCreateDTO(
                category=LocationCategory.TENNIS,
                address="вул. 1",
                price_per_hour=100.0,
            )

    def test_missing_address_raises(self):
        with pytest.raises(ValidationError):
            LocationCreateDTO(
                name="Корт",
                category=LocationCategory.TENNIS,
                price_per_hour=100.0,
            )

    def test_large_price_ok(self):
        dto = LocationCreateDTO(
            name="VIP Корт",
            category=LocationCategory.TENNIS,
            address="вул. Преміум 1",
            price_per_hour=9999.99,
        )
        assert dto.price_per_hour == pytest.approx(9999.99)

    def test_description_optional(self):
        dto = LocationCreateDTO(
            name="Корт",
            category=LocationCategory.GYM,
            address="вул. 1",
            price_per_hour=100.0,
        )
        assert dto.description is None


class TestLocationUpdateDTO:
    def test_all_fields_optional(self):
        dto = LocationUpdateDTO()
        assert dto.name is None
        assert dto.price_per_hour is None

    def test_update_price_only(self):
        dto = LocationUpdateDTO(price_per_hour=500.0)
        assert dto.price_per_hour == pytest.approx(500.0)

    def test_update_name_only(self):
        dto = LocationUpdateDTO(name="Новий корт")
        assert dto.name == "Новий корт"


class TestSlotCreateDTO:
    def test_valid_slot(self):
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=2)
        dto = SlotCreateDTO(location_id=1, start_time=start, end_time=end)
        assert dto.location_id == 1

    def test_end_before_start_raises(self):
        start = datetime.now(timezone.utc) + timedelta(hours=3)
        end = datetime.now(timezone.utc) + timedelta(hours=1)
        with pytest.raises(ValidationError):
            SlotCreateDTO(location_id=1, start_time=start, end_time=end)

    def test_end_equals_start_raises(self):
        t = datetime.now(timezone.utc) + timedelta(hours=2)
        with pytest.raises(ValidationError):
            SlotCreateDTO(location_id=1, start_time=t, end_time=t)

    def test_one_hour_slot_ok(self):
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=1)
        dto = SlotCreateDTO(location_id=1, start_time=start, end_time=end)
        assert (dto.end_time - dto.start_time).seconds == 3600

    def test_long_slot_ok(self):
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=8)
        dto = SlotCreateDTO(location_id=1, start_time=start, end_time=end)
        assert dto.location_id == 1

    def test_missing_location_id_raises(self):
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=2)
        with pytest.raises(ValidationError):
            SlotCreateDTO(start_time=start, end_time=end)


class TestBookingCreateDTO:
    def test_minimal_booking(self):
        dto = BookingCreateDTO(slot_id=1)
        assert dto.slot_id == 1
        assert dto.notes is None

    def test_with_all_fields(self):
        dto = BookingCreateDTO(
            slot_id=1,
            notes="Прошу підготувати корт",
            guest_name="Іван",
            guest_email="ivan@test.com",
            guest_phone="+380501234567",
        )
        assert dto.guest_name == "Іван"
        assert dto.guest_email == "ivan@test.com"

    def test_missing_slot_id_raises(self):
        with pytest.raises(ValidationError):
            BookingCreateDTO()


class TestBookingStatusUpdateDTO:
    def test_valid_status(self):
        dto = BookingStatusUpdateDTO(status=BookingStatus.CONFIRMED)
        assert dto.status == BookingStatus.CONFIRMED

    def test_all_statuses_valid(self):
        for status in BookingStatus:
            dto = BookingStatusUpdateDTO(status=status)
            assert dto.status == status

    def test_invalid_status_raises(self):
        with pytest.raises(ValidationError):
            BookingStatusUpdateDTO(status="unknown_status")
