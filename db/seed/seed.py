"""
Seed script - заповнює БД тестовими даними
Запуск: python db/seed/seed.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from src.config.database import SessionLocal, engine
from src.config.database import Base
from src.models.user import User, UserRole
from src.models.location import Location, LocationCategory, LocationImage
from src.models.slot import Slot, SlotStatus
from src.models.booking import Booking

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Очистити таблиці
db.query(Booking).delete()
db.query(Slot).delete()
db.query(LocationImage).delete()
db.query(Location).delete()
db.query(User).delete()
db.commit()

# Користувачі
admin = User(
    email="admin@sportbook.ua",
    full_name="Адміністратор",
    hashed_password=pwd_context.hash("admin123"),
    role=UserRole.ADMIN,
    phone="+380501234567",
)
user1 = User(
    email="ivan@example.com",
    full_name="Іван Петренко",
    hashed_password=pwd_context.hash("user123"),
    role=UserRole.USER,
    phone="+380671234567",
)
db.add_all([admin, user1])
db.commit()

# Локації
locations_data = [
    {"name": "Тенісний корт №1", "category": LocationCategory.TENNIS, "address": "вул. Спортивна 1, Київ", "price_per_hour": 300.0, "description": "Відкритий тенісний корт з твердим покриттям"},
    {"name": "Футбольне поле А", "category": LocationCategory.FOOTBALL, "address": "вул. Стадіонна 5, Київ", "price_per_hour": 800.0, "description": "Футбольне поле зі штучним газоном"},
    {"name": "Басейн олімпійський", "category": LocationCategory.POOL, "address": "просп. Перемоги 10, Київ", "price_per_hour": 500.0, "description": "50-метровий олімпійський басейн"},
    {"name": "Тренажерний зал FitPro", "category": LocationCategory.GYM, "address": "вул. Здоров'я 3, Київ", "price_per_hour": 200.0, "description": "Сучасний тренажерний зал з новим обладнанням"},
]

locations = []
for data in locations_data:
    loc = Location(**data, capacity=10)
    db.add(loc)
    locations.append(loc)
db.commit()

# Слоти на наступні 7 днів
now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
for loc in locations:
    for day in range(7):
        for hour in [9, 11, 13, 15, 17, 19]:
            start = now + timedelta(days=day+1, hours=hour)
            end = start + timedelta(hours=2)
            slot = Slot(location_id=loc.id, start_time=start, end_time=end, status=SlotStatus.AVAILABLE)
            db.add(slot)

db.commit()
db.close()
print("✅ Seed завершено успішно!")
print("   Admin: admin@sportbook.ua / admin123")
print("   User:  ivan@example.com / user123")
