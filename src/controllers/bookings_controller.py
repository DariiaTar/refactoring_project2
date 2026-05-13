from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.config.dependencies import get_current_user, require_admin
from src.services.booking_service import BookingService
from src.models.user import User
from src.dto.booking_dto import (
    BookingCreateDTO, BookingResponseDTO, BookingStatusUpdateDTO,
    BookingAdminResponseDTO, BookingDetailsResponseDTO,
)

router = APIRouter()

DbDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
AdminDep = Annotated[User, Depends(require_admin)]


@router.post("/", response_model=BookingResponseDTO, summary="Створити бронювання")
def create_booking(data: BookingCreateDTO, db: DbDep, current_user: CurrentUserDep):
    return BookingService(db).create_booking(current_user.id, data)


@router.get("/my", response_model=List[BookingResponseDTO], summary="Мої бронювання")
def my_bookings(db: DbDep, current_user: CurrentUserDep):
    return BookingService(db).get_user_bookings(current_user.id)


@router.get("/", response_model=List[BookingAdminResponseDTO], summary="Всі бронювання (адмін)")
def all_bookings(db: DbDep, _: AdminDep):
    return BookingService(db).get_all_bookings_admin()


@router.get("/{booking_id}", response_model=BookingDetailsResponseDTO, summary="Деталі бронювання")
def booking_details(booking_id: int, db: DbDep, current_user: CurrentUserDep):
    is_admin = current_user.role.value == "admin"
    return BookingService(db).get_booking(booking_id, current_user.id, is_admin)


@router.post("/{booking_id}/pay", response_model=BookingDetailsResponseDTO, summary="Оплатити бронювання")
def pay_booking(booking_id: int, db: DbDep, current_user: CurrentUserDep):
    is_admin = current_user.role.value == "admin"
    return BookingService(db).pay_booking(booking_id, current_user.id, is_admin)


@router.post("/{booking_id}/cancel", response_model=BookingResponseDTO, summary="Скасувати бронювання")
def cancel_booking(booking_id: int, db: DbDep, current_user: CurrentUserDep):
    is_admin = current_user.role.value == "admin"
    return BookingService(db).cancel_booking(booking_id, current_user.id, is_admin)


@router.put("/{booking_id}/status", response_model=BookingResponseDTO, summary="Змінити статус (адмін)")
def update_status(booking_id: int, data: BookingStatusUpdateDTO, db: DbDep, _: AdminDep):
    return BookingService(db).update_status(booking_id, data.status)
