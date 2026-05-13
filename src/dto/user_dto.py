from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from src.models.user import UserRole
import re


class UserRegisterDTO(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    phone: Optional[str] = None

    @validator("password")
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError("Пароль має містити мінімум 6 символів")
        return v

    @validator("full_name")
    def full_name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Ім'я не може бути порожнім")
        return v

    @validator("phone", pre=True, always=True)
    def phone_format(cls, v):
        if v is None:
            return v
        phone_pattern = r'^[+]?\d{7,15}$'
        if not re.match(phone_pattern, v.replace(" ", "").replace("-", "")):
            raise ValueError("Телефон має містити 7-15 цифр (можна з +)")
        return v


class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str


class UserResponseDTO(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponseDTO


class UserUpdateDTO(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
