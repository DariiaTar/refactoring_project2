from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from src.models.slot import SlotStatus
from src.models.booking import BookingStatus


class SlotCreateDTO(BaseModel):
    location_id: int
    start_time: datetime
    end_time: datetime

    @validator("end_time")
    def end_after_start(cls, v, values):
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("Час завершення має бути після початку")
        return v


class SlotResponseDTO(BaseModel):
    id: int
    location_id: int
    start_time: datetime
    end_time: datetime
    status: SlotStatus

    class Config:
        from_attributes = True


class BookingCreateDTO(BaseModel):
    slot_id: int
    notes: Optional[str] = None
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None


class BookingResponseDTO(BaseModel):
    id: int
    slot_id: int
    status: BookingStatus
    total_price: float
    notes: Optional[str] = None
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BookingStatusUpdateDTO(BaseModel):
    status: BookingStatus


class BookingAdminResponseDTO(BaseModel):
    id: int
    slot_id: int
    user_id: int
    user_full_name: str
    user_phone: Optional[str] = None
    location_id: int
    location_name: str
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    total_price: float
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BookingDetailsResponseDTO(BaseModel):
    id: int
    slot_id: int
    status: BookingStatus
    total_price: float
    notes: Optional[str] = None
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None
    created_at: datetime
    user_id: int
    user_full_name: str
    user_phone: Optional[str] = None
    location_id: int
    location_name: str
    location_address: str
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True
