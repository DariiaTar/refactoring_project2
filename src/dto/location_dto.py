from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from src.models.location import LocationCategory


class LocationImageDTO(BaseModel):
    id: int
    image_url: str
    is_primary: bool

    class Config:
        from_attributes = True


class LocationCreateDTO(BaseModel):
    name: str
    description: Optional[str] = None
    category: LocationCategory
    address: str
    price_per_hour: float
    capacity: int = 1

    @validator("price_per_hour")
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError("Ціна має бути більше 0")
        return v

    @validator("capacity")
    def capacity_positive(cls, v):
        if v < 1:
            raise ValueError("Місткість має бути мінімум 1")
        return v


class LocationUpdateDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[LocationCategory] = None
    address: Optional[str] = None
    price_per_hour: Optional[float] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None


class LocationResponseDTO(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: LocationCategory
    address: str
    price_per_hour: float
    capacity: int
    is_active: bool
    images: List[LocationImageDTO] = []
    created_at: datetime

    class Config:
        from_attributes = True
