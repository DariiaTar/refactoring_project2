import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException
from datetime import datetime, timezone

from src.services.location_service import LocationService
from src.models.location import Location, LocationCategory, LocationImage
from src.dto.location_dto import LocationCreateDTO, LocationUpdateDTO


def make_location(id=1, name="Тенісний корт", is_active=True, price=300.0, category=LocationCategory.TENNIS):
    loc = Location()
    loc.id = id
    loc.name = name
    loc.description = "Опис"
    loc.category = category
    loc.address = "вул. Спортивна 1"
    loc.price_per_hour = price
    loc.capacity = 4
    loc.is_active = is_active
    loc.images = []
    loc.created_at = datetime.now(timezone.utc)
    loc.updated_at = datetime.now(timezone.utc)
    return loc


def make_image(id=1, location_id=1, url="/uploads/test.jpg", is_primary=False):
    img = LocationImage()
    img.id = id
    img.location_id = location_id
    img.image_url = url
    img.is_primary = is_primary
    img.created_at = datetime.now(timezone.utc)
    return img


@pytest.fixture
def location_service():
    db = MagicMock()
    return LocationService(db)


class TestGetById:
    def test_returns_location_when_found(self, location_service):
        loc = make_location()
        location_service.repo.get_by_id = MagicMock(return_value=loc)
        result = location_service.get_by_id(1)
        assert result.name == "Тенісний корт"

    def test_raises_404_when_not_found(self, location_service):
        location_service.repo.get_by_id = MagicMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            location_service.get_by_id(999)
        assert exc.value.status_code == 404

    def test_raises_404_message_contains_keyword(self, location_service):
        location_service.repo.get_by_id = MagicMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            location_service.get_by_id(1)
        assert "локацію" in exc.value.detail.lower()

    def test_returns_dto_with_images(self, location_service):
        loc = make_location()
        loc.images = [make_image()]
        location_service.repo.get_by_id = MagicMock(return_value=loc)
        result = location_service.get_by_id(1)
        assert hasattr(result, "images")

    def test_returns_dto_with_correct_price(self, location_service):
        loc = make_location(price=500.0)
        location_service.repo.get_by_id = MagicMock(return_value=loc)
        result = location_service.get_by_id(1)
        assert result.price_per_hour == pytest.approx(500.0)


class TestGetAll:
    def test_returns_all_locations(self, location_service):
        locs = [make_location(1), make_location(2, name="Басейн")]
        location_service.repo.get_all = MagicMock(return_value=locs)
        result = location_service.get_all()
        assert len(result) == 2

    def test_returns_empty_list_when_no_locations(self, location_service):
        location_service.repo.get_all = MagicMock(return_value=[])
        result = location_service.get_all()
        assert result == []

    def test_passes_category_filter_to_repo(self, location_service):
        location_service.repo.get_all = MagicMock(return_value=[])
        location_service.get_all(category=LocationCategory.TENNIS)
        location_service.repo.get_all.assert_called_once_with(
            category=LocationCategory.TENNIS, active_only=True
        )

    def test_active_only_true_by_default(self, location_service):
        location_service.repo.get_all = MagicMock(return_value=[])
        location_service.get_all()
        call_kwargs = location_service.repo.get_all.call_args[1]
        assert call_kwargs.get("active_only") is True

    def test_get_all_no_category_filter(self, location_service):
        location_service.repo.get_all = MagicMock(return_value=[])
        location_service.get_all(category=None)
        call_kwargs = location_service.repo.get_all.call_args[1]
        assert call_kwargs.get("category") is None

    def test_get_all_inactive_included_when_active_only_false(self, location_service):
        loc = make_location(is_active=False)
        location_service.repo.get_all = MagicMock(return_value=[loc])
        result = location_service.get_all(active_only=False)
        assert len(result) == 1


class TestCreate:
    def test_creates_location_successfully(self, location_service):
        loc = make_location()
        location_service.repo.create = MagicMock(return_value=loc)
        data = LocationCreateDTO(
            name="Корт",
            category=LocationCategory.TENNIS,
            address="вул. 1",
            price_per_hour=200.0,
        )
        result = location_service.create(data)
        assert result.name == "Тенісний корт"
        location_service.repo.create.assert_called_once()

    def test_create_returns_dto(self, location_service):
        loc = make_location()
        location_service.repo.create = MagicMock(return_value=loc)
        data = LocationCreateDTO(
            name="Корт",
            category=LocationCategory.TENNIS,
            address="вул. 1",
            price_per_hour=500.0,
        )
        result = location_service.create(data)
        assert hasattr(result, "id")
        assert hasattr(result, "price_per_hour")

    def test_create_gym_location(self, location_service):
        loc = make_location(category=LocationCategory.GYM)
        location_service.repo.create = MagicMock(return_value=loc)
        data = LocationCreateDTO(
            name="Тренажерний зал",
            category=LocationCategory.GYM,
            address="вул. 1",
            price_per_hour=150.0,
        )
        result = location_service.create(data)
        assert result.category == LocationCategory.GYM

    def test_create_passes_all_fields_to_repo(self, location_service):
        loc = make_location()
        location_service.repo.create = MagicMock(return_value=loc)
        data = LocationCreateDTO(
            name="Корт",
            category=LocationCategory.FOOTBALL,
            address="вул. Футбольна 5",
            price_per_hour=400.0,
            description="Великий футбольний майданчик",
            capacity=22,
        )
        location_service.create(data)
        location_service.repo.create.assert_called_once()


class TestUpdate:
    def test_updates_existing_location(self, location_service):
        loc = make_location()
        updated = make_location(name="Оновлений Корт")
        location_service.repo.get_by_id = MagicMock(return_value=loc)
        location_service.repo.update = MagicMock(return_value=updated)

        data = LocationUpdateDTO(name="Оновлений Корт")
        result = location_service.update(1, data)
        assert result.name == "Оновлений Корт"

    def test_update_raises_404_when_not_found(self, location_service):
        location_service.repo.get_by_id = MagicMock(return_value=None)
        data = LocationUpdateDTO(name="Нова назва")
        with pytest.raises(HTTPException) as exc:
            location_service.update(999, data)
        assert exc.value.status_code == 404

    def test_update_calls_repo_update(self, location_service):
        loc = make_location()
        updated = make_location()
        location_service.repo.get_by_id = MagicMock(return_value=loc)
        location_service.repo.update = MagicMock(return_value=updated)

        data = LocationUpdateDTO(price_per_hour=999.0)
        location_service.update(1, data)
        location_service.repo.update.assert_called_once()

    def test_update_price(self, location_service):
        loc = make_location()
        updated = make_location(price=999.0)
        location_service.repo.get_by_id = MagicMock(return_value=loc)
        location_service.repo.update = MagicMock(return_value=updated)

        data = LocationUpdateDTO(price_per_hour=999.0)
        result = location_service.update(1, data)
        assert result.price_per_hour == pytest.approx(999.0)


class TestDelete:
    def test_deletes_existing_location(self, location_service):
        loc = make_location()
        location_service.repo.get_by_id = MagicMock(return_value=loc)
        location_service.repo.delete = MagicMock()
        location_service.delete(1)
        location_service.repo.delete.assert_called_once_with(loc)

    def test_delete_raises_404_when_not_found(self, location_service):
        location_service.repo.get_by_id = MagicMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            location_service.delete(999)
        assert exc.value.status_code == 404

    def test_delete_calls_repo_with_correct_object(self, location_service):
        loc = make_location(id=5)
        location_service.repo.get_by_id = MagicMock(return_value=loc)
        location_service.repo.delete = MagicMock()
        location_service.delete(5)
        location_service.repo.delete.assert_called_once_with(loc)


class TestUploadImage:
    @pytest.mark.asyncio
    async def test_upload_invalid_content_type_raises(self, location_service):
        loc = make_location()
        location_service.repo.get_by_id = MagicMock(return_value=loc)
        file = MagicMock()
        file.content_type = "application/pdf"
        file.read = AsyncMock(return_value=b"data")
        file.filename = "doc.pdf"
        with pytest.raises(HTTPException) as exc:
            await location_service.upload_image(1, file)
        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_location_not_found_raises(self, location_service):
        location_service.repo.get_by_id = MagicMock(return_value=None)
        file = MagicMock()
        with pytest.raises(HTTPException) as exc:
            await location_service.upload_image(999, file)
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_upload_too_large_file_raises(self, location_service):
        loc = make_location()
        location_service.repo.get_by_id = MagicMock(return_value=loc)
        file = MagicMock()
        file.content_type = "image/jpeg"
        file.filename = "big.jpg"
        file.read = AsyncMock(return_value=b"x" * (6 * 1024 * 1024))
        with pytest.raises(HTTPException) as exc:
            await location_service.upload_image(1, file)
        assert exc.value.status_code == 400


class TestDeleteImage:
    def test_delete_image_calls_repo(self, location_service):
        location_service.repo.delete_image = MagicMock()
        location_service.delete_image(1)
        location_service.repo.delete_image.assert_called_once_with(1)
