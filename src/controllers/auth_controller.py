from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.config.dependencies import get_current_user
from src.services.auth_service import AuthService
from src.dto.user_dto import UserRegisterDTO, UserLoginDTO, TokenDTO, UserResponseDTO
from src.models.user import User

router = APIRouter()

DbDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.post("/register", response_model=TokenDTO, summary="Реєстрація")
def register(data: UserRegisterDTO, db: DbDep):
    return AuthService(db).register(data)


@router.post("/login", response_model=TokenDTO, summary="Вхід")
def login(data: UserLoginDTO, db: DbDep):
    return AuthService(db).login(data)


@router.get("/me", response_model=UserResponseDTO, summary="Поточний користувач")
def me(current_user: CurrentUserDep):
    return current_user
