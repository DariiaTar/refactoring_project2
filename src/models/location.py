from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from src.config.database import Base


class LocationCategory(str, enum.Enum):
    TENNIS = "tennis"
    FOOTBALL = "football"
    POOL = "pool"
    GYM = "gym"
    OTHER = "other"


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(LocationCategory), nullable=False)
    address = Column(String, nullable=False)
    price_per_hour = Column(Float, nullable=False)
    capacity = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    images = relationship("LocationImage", back_populates="location", cascade="all, delete-orphan")
    slots = relationship("Slot", back_populates="location", cascade="all, delete-orphan")


class LocationImage(Base):
    __tablename__ = "location_images"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    image_url = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    location = relationship("Location", back_populates="images")
