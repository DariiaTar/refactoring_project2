from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.config.database import get_db
from src.config.dependencies import get_current_user, require_admin
from src.repositories.user_repository import UserRepository
from src.models.user import User
from src.dto.user_dto import UserResponseDTO, UserUpdateDTO

router = APIRouter()


@router.get("/", response_model=List[UserResponseDTO], summary="Всі користувачі (адмін)")
def get_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return UserRepository(db).get_all()


@router.put("/me", response_model=UserResponseDTO, summary="Оновити профіль")
def update_me(
    data: UserUpdateDTO,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    return repo.update(current_user, **data.dict(exclude_none=True))


@router.put("/{user_id}/deactivate", summary="Заблокувати користувача (адмін)")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    repo.update(user, is_active=False)
    return {"message": "Користувача заблоковано"}
