from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.config.dependencies import require_admin
from src.services.location_service import LocationService
from src.models.location import LocationCategory
from src.models.user import User
from src.dto.location_dto import LocationCreateDTO, LocationUpdateDTO, LocationResponseDTO

router = APIRouter()

DbDep = Annotated[Session, Depends(get_db)]
AdminDep = Annotated[User, Depends(require_admin)]


@router.get("/", response_model=List[LocationResponseDTO], summary="Список локацій")
def get_locations(db: DbDep, category: Optional[LocationCategory] = Query(None)):
    return LocationService(db).get_all(category=category)


@router.get("/{location_id}", response_model=LocationResponseDTO, summary="Деталі локації")
def get_location(location_id: int, db: DbDep):
    return LocationService(db).get_by_id(location_id)


@router.post("/", response_model=LocationResponseDTO, summary="Створити локацію (адмін)")
def create_location(data: LocationCreateDTO, db: DbDep, _: AdminDep):
    return LocationService(db).create(data)


@router.put("/{location_id}", response_model=LocationResponseDTO, summary="Оновити локацію (адмін)")
def update_location(location_id: int, data: LocationUpdateDTO, db: DbDep, _: AdminDep):
    return LocationService(db).update(location_id, data)


@router.delete("/{location_id}", summary="Видалити локацію (адмін)")
def delete_location(location_id: int, db: DbDep, _: AdminDep):
    LocationService(db).delete(location_id)
    return {"message": "Локацію видалено"}


@router.post("/{location_id}/images", summary="Завантажити фото (адмін)")
async def upload_image(
    location_id: int,
    db: DbDep,
    _: AdminDep,
    file: UploadFile = File(...),
    is_primary: bool = False,
):
    return await LocationService(db).upload_image(location_id, file, is_primary)


@router.delete("/images/{image_id}", summary="Видалити фото (адмін)")
def delete_image(image_id: int, db: DbDep, _: AdminDep):
    LocationService(db).delete_image(image_id)
    return {"message": "Фото видалено"}
