from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.config.dependencies import get_current_user, require_admin
from src.repositories.user_repository import UserRepository
from src.models.user import User
from src.dto.user_dto import UserResponseDTO, UserUpdateDTO

router = APIRouter()

DbDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
AdminDep = Annotated[User, Depends(require_admin)]


@router.get("/", response_model=List[UserResponseDTO], summary="Всі користувачі (адмін)")
def get_users(db: DbDep, _: AdminDep):
    return UserRepository(db).get_all()


@router.put("/me", response_model=UserResponseDTO, summary="Оновити профіль")
def update_me(data: UserUpdateDTO, db: DbDep, current_user: CurrentUserDep):
    repo = UserRepository(db)
    return repo.update(current_user, **data.dict(exclude_none=True))


@router.put(
    "/{user_id}/deactivate",
    summary="Заблокувати користувача (адмін)",
    responses={404: {"description": "Користувача не знайдено"}},
)
def deactivate_user(user_id: int, db: DbDep, _: AdminDep):
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    repo.update(user, is_active=False)
    return {"message": "Користувача заблоковано"}
