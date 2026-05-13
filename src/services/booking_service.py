from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from src.repositories.slot_repository import SlotRepository
from src.repositories.booking_repository import BookingRepository
from src.repositories.location_repository import LocationRepository
from src.models.slot import SlotStatus
from src.models.booking import BookingStatus
from src.dto.booking_dto import (
    BookingCreateDTO, BookingResponseDTO, SlotCreateDTO, SlotResponseDTO,
    BookingAdminResponseDTO, BookingDetailsResponseDTO,
)
from src.services.pricing_strategy import IPricingStrategy, DynamicPricingContext
from src.services.booking_observer import IBookingObserver, BookingNotifier

_ERR_SLOT_NOT_FOUND = "Слот не знайдено"
_ERR_BOOKING_NOT_FOUND = "Бронювання не знайдено"
_ERR_LOCATION_NOT_FOUND = "Локацію не знайдено"
_ERR_ACCESS_DENIED = "Доступ заборонено"


class SlotService:
    def __init__(self, db: Session):
        self.slot_repo = SlotRepository(db)
        self.location_repo = LocationRepository(db)

    def get_by_location(self, location_id: int) -> List[SlotResponseDTO]:
        slots = self.slot_repo.get_by_location(location_id)
        return [SlotResponseDTO.from_orm(s) for s in slots]

    def get_available(self, location_id: int) -> List[SlotResponseDTO]:
        slots = self.slot_repo.get_available_by_location(location_id)
        return [SlotResponseDTO.from_orm(s) for s in slots]

    def create(self, data: SlotCreateDTO) -> SlotResponseDTO:
        location = self.location_repo.get_by_id(data.location_id)
        if not location:
            raise HTTPException(status_code=404, detail=_ERR_LOCATION_NOT_FOUND)
        slot = self.slot_repo.create(data.location_id, data.start_time, data.end_time)
        return SlotResponseDTO.from_orm(slot)

    def delete(self, slot_id: int) -> None:
        slot = self.slot_repo.get_by_id(slot_id)
        if not slot:
            raise HTTPException(status_code=404, detail=_ERR_SLOT_NOT_FOUND)
        if slot.status == SlotStatus.BOOKED:
            raise HTTPException(status_code=400, detail="Не можна видалити заброньований слот")
        self.slot_repo.delete(slot)


class BookingService:
    def __init__(
        self,
        db: Session,
        pricing_strategy: Optional[IPricingStrategy] = None,
        observers: Optional[List[IBookingObserver]] = None,
    ):
        self.booking_repo = BookingRepository(db)
        self.slot_repo = SlotRepository(db)
        self.location_repo = LocationRepository(db)
        self._pricing_context = DynamicPricingContext(pricing_strategy)
        self._notifier = BookingNotifier()
        for obs in (observers or []):
            self._notifier.subscribe(obs)

    def set_pricing_strategy(self, strategy: IPricingStrategy) -> None:
        self._pricing_context.set_strategy(strategy)

    def add_observer(self, observer: IBookingObserver) -> None:
        self._notifier.subscribe(observer)

    def remove_observer(self, observer: IBookingObserver) -> None:
        self._notifier.unsubscribe(observer)

    def create_booking(self, user_id: int, data: BookingCreateDTO) -> BookingResponseDTO:
        slot = self.slot_repo.get_by_id(data.slot_id)
        if not slot:
            raise HTTPException(status_code=404, detail=_ERR_SLOT_NOT_FOUND)
        if slot.status != SlotStatus.AVAILABLE:
            raise HTTPException(status_code=400, detail="Слот вже заброньований")

        location = self.location_repo.get_by_id(slot.location_id)
        total_price = self._pricing_context.calculate_price(
            location.price_per_hour, slot.start_time, slot.end_time
        )

        booking = self.booking_repo.create(
            user_id=user_id,
            slot_id=data.slot_id,
            total_price=total_price,
            notes=data.notes,
            guest_name=data.guest_name,
            guest_email=data.guest_email,
            guest_phone=data.guest_phone,
        )
        self.slot_repo.update_status(slot, SlotStatus.BOOKED)
        self._notifier.notify_booking_created(booking.id, user_id, data.slot_id, total_price)
        return BookingResponseDTO.from_orm(booking)

    def get_user_bookings(self, user_id: int) -> List[BookingResponseDTO]:
        bookings = self.booking_repo.get_by_user(user_id)
        return [BookingResponseDTO.from_orm(b) for b in bookings]

    def get_all_bookings(self) -> List[BookingResponseDTO]:
        bookings = self.booking_repo.get_all()
        return [BookingResponseDTO.from_orm(b) for b in bookings]

    def get_all_bookings_admin(self) -> List[BookingAdminResponseDTO]:
        """Get all bookings with location and user details for admin panel"""
        bookings = self.booking_repo.get_all()
        admin_bookings = []
        for b in bookings:
            location = self.location_repo.get_by_id(b.slot.location_id)
            admin_booking = BookingAdminResponseDTO(
                id=b.id,
                slot_id=b.slot_id,
                user_id=b.user_id,
                user_full_name=b.user.full_name,
                user_phone=b.user.phone,
                location_id=b.slot.location_id,
                location_name=location.name,
                start_time=b.slot.start_time,
                end_time=b.slot.end_time,
                status=b.status,
                total_price=b.total_price,
                notes=b.notes,
                created_at=b.created_at,
            )
            admin_bookings.append(admin_booking)
        return admin_bookings

    def get_booking(  # noqa: E501
        self, booking_id: int, user_id: Optional[int] = None, is_admin: bool = False
    ) -> BookingDetailsResponseDTO:
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail=_ERR_BOOKING_NOT_FOUND)
        if not is_admin and booking.user_id != user_id:
            raise HTTPException(status_code=403, detail=_ERR_ACCESS_DENIED)

        location = self.location_repo.get_by_id(booking.slot.location_id)
        return BookingDetailsResponseDTO(
            id=booking.id,
            slot_id=booking.slot_id,
            status=booking.status,
            total_price=booking.total_price,
            notes=booking.notes,
            guest_name=booking.guest_name,
            guest_email=booking.guest_email,
            guest_phone=booking.guest_phone,
            created_at=booking.created_at,
            user_id=booking.user_id,
            user_full_name=booking.user.full_name,
            user_phone=booking.user.phone,
            location_id=booking.slot.location_id,
            location_name=location.name,
            location_address=location.address,
            start_time=booking.slot.start_time,
            end_time=booking.slot.end_time,
        )

    def pay_booking(  # noqa: E501
        self, booking_id: int, user_id: Optional[int] = None, is_admin: bool = False
    ) -> BookingDetailsResponseDTO:
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail=_ERR_BOOKING_NOT_FOUND)
        if not is_admin and booking.user_id != user_id:
            raise HTTPException(status_code=403, detail=_ERR_ACCESS_DENIED)
        if booking.status != BookingStatus.PENDING_PAYMENT:
            raise HTTPException(status_code=400, detail="Бронювання не потребує оплати")

        updated = self.booking_repo.update_status(booking, BookingStatus.CONFIRMED)
        self._notifier.notify_booking_confirmed(booking_id, updated.user_id)
        location = self.location_repo.get_by_id(updated.slot.location_id)
        return BookingDetailsResponseDTO(
            id=updated.id,
            slot_id=updated.slot_id,
            status=updated.status,
            total_price=updated.total_price,
            notes=updated.notes,
            guest_name=updated.guest_name,
            guest_email=updated.guest_email,
            guest_phone=updated.guest_phone,
            created_at=updated.created_at,
            user_id=updated.user_id,
            user_full_name=updated.user.full_name,
            user_phone=updated.user.phone,
            location_id=updated.slot.location_id,
            location_name=location.name,
            location_address=location.address,
            start_time=updated.slot.start_time,
            end_time=updated.slot.end_time,
        )

    def cancel_booking(self, booking_id: int, user_id: int, is_admin: bool = False) -> BookingResponseDTO:
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail=_ERR_BOOKING_NOT_FOUND)
        if not is_admin and booking.user_id != user_id:
            raise HTTPException(status_code=403, detail=_ERR_ACCESS_DENIED)
        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Бронювання вже скасовано")

        updated = self.booking_repo.update_status(booking, BookingStatus.CANCELLED)
        self.slot_repo.update_status(booking.slot, SlotStatus.AVAILABLE)
        self._notifier.notify_booking_cancelled(booking_id, user_id)
        return BookingResponseDTO.from_orm(updated)

    def update_status(self, booking_id: int, status: BookingStatus) -> BookingResponseDTO:
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail=_ERR_BOOKING_NOT_FOUND)
        updated = self.booking_repo.update_status(booking, status)
        return BookingResponseDTO.from_orm(updated)
