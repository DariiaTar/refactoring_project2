from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from src.controllers.auth_controller import router as auth_router
from src.controllers.locations_controller import router as locations_router
from src.controllers.slots_controller import router as slots_router
from src.controllers.bookings_controller import router as bookings_router
from src.controllers.users_controller import router as users_router

app = FastAPI(
    title="SportBook UA",
    description="Система бронювання спортивних локацій",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Serve uploaded images
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_router, prefix="/api/auth", tags=["Автентифікація"])
app.include_router(locations_router, prefix="/api/locations", tags=["Локації"])
app.include_router(slots_router, prefix="/api/slots", tags=["Слоти"])
app.include_router(bookings_router, prefix="/api/bookings", tags=["Бронювання"])
app.include_router(users_router, prefix="/api/users", tags=["Користувачі"])


@app.get("/")
def root():
    return {"message": "SportBook UA API", "version": "1.0.0"}
