import os
import uuid
import aiofiles
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional

from src.repositories.location_repository import LocationRepository
from src.models.location import LocationCategory
from src.dto.location_dto import LocationCreateDTO, LocationUpdateDTO, LocationResponseDTO
from src.config.settings import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_IMAGE_TYPES


_LOCATION_NOT_FOUND = "Локацію не знайдено"


class LocationService:
    def __init__(self, db: Session):
        self.repo = LocationRepository(db)

    def get_all(self, category: Optional[LocationCategory] = None, active_only: bool = True) -> List[LocationResponseDTO]:  # noqa: E501
        locations = self.repo.get_all(category=category, active_only=active_only)
        return [LocationResponseDTO.from_orm(loc) for loc in locations]

    def get_by_id(self, location_id: int) -> LocationResponseDTO:
        location = self.repo.get_by_id(location_id)
        if not location:
            raise HTTPException(status_code=404, detail=_LOCATION_NOT_FOUND)
        return LocationResponseDTO.from_orm(location)

    def create(self, data: LocationCreateDTO) -> LocationResponseDTO:
        location = self.repo.create(**data.dict())
        return LocationResponseDTO.from_orm(location)

    def update(self, location_id: int, data: LocationUpdateDTO) -> LocationResponseDTO:
        location = self.repo.get_by_id(location_id)
        if not location:
            raise HTTPException(status_code=404, detail=_LOCATION_NOT_FOUND)
        updated = self.repo.update(location, **data.dict(exclude_none=True))
        return LocationResponseDTO.from_orm(updated)

    def delete(self, location_id: int) -> None:
        location = self.repo.get_by_id(location_id)
        if not location:
            raise HTTPException(status_code=404, detail=_LOCATION_NOT_FOUND)
        self.repo.delete(location)

    async def upload_image(self, location_id: int, file: UploadFile, is_primary: bool = False) -> dict:
        location = self.repo.get_by_id(location_id)
        if not location:
            raise HTTPException(status_code=404, detail=_LOCATION_NOT_FOUND)

        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="Дозволені лише JPEG, PNG, WEBP")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Файл перевищує 5MB")

        content_type_to_ext = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
        }
        ext = content_type_to_ext.get(file.content_type, "jpg")
        filename = f"{uuid.uuid4()}.{ext}"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filepath = os.path.join(UPLOAD_DIR, filename)

        async with aiofiles.open(filepath, "wb") as f:
            await f.write(content)

        image_url = f"/uploads/{filename}"
        image = self.repo.add_image(location_id, image_url, is_primary)
        return {"id": image.id, "image_url": image_url, "is_primary": image.is_primary}

    def delete_image(self, image_id: int) -> None:
        self.repo.delete_image(image_id)
