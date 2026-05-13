import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.config.database import Base, get_db

TEST_DB_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_token(client):
    client.post("/api/auth/register", json={
        "email": "admin@test.ua",
        "full_name": "Адмін",
        "password": "admin123"  # NOSONAR
    })
    db = TestingSessionLocal()
    from src.models.user import User, UserRole
    user = db.query(User).filter(User.email == "admin@test.ua").first()
    user.role = UserRole.ADMIN
    db.commit()
    db.close()

    resp = client.post("/api/auth/login", json={"email": "admin@test.ua", "password": "admin123"})  # NOSONAR
    return resp.json()["access_token"]


@pytest.fixture
def user_token(client):
    client.post("/api/auth/register", json={
        "email": "user@test.ua",
        "full_name": "Користувач",
        "password": "user123"  # NOSONAR
    })
    resp = client.post("/api/auth/login", json={"email": "user@test.ua", "password": "user123"})  # NOSONAR
    return resp.json()["access_token"]


# --- Scenario 1: Реєстрація та вхід ---
class TestAuthFlow:
    def test_register_and_login(self, client):
        r = client.post("/api/auth/register", json={
            "email": "new@test.ua", "full_name": "Новий", "password": "pass123"  # NOSONAR
        })
        assert r.status_code == 200
        assert "access_token" in r.json()

        r2 = client.post("/api/auth/login", json={"email": "new@test.ua", "password": "pass123"})  # NOSONAR
        assert r2.status_code == 200

    def test_login_wrong_password(self, client):
        client.post("/api/auth/register", json={
            "email": "user2@test.ua", "full_name": "Юзер", "password": "correct"  # NOSONAR
        })
        r = client.post("/api/auth/login", json={"email": "user2@test.ua", "password": "wrong"})  # NOSONAR
        assert r.status_code == 401

    def test_me_requires_auth(self, client):
        r = client.get("/api/auth/me")
        assert r.status_code == 403


# --- Scenario 2: Успішне бронювання ---
class TestBookingFlow:
    def test_successful_booking(self, client, admin_token, user_token):
        # Адмін створює локацію
        r = client.post("/api/locations/", json={
            "name": "Корт А", "category": "tennis",
            "address": "вул. 1", "price_per_hour": 300.0
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        location_id = r.json()["id"]

        # Адмін створює слот
        from datetime import datetime, timezone, timedelta
        start = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        end = (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat()
        r2 = client.post("/api/slots/", json={
            "location_id": location_id, "start_time": start, "end_time": end
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert r2.status_code == 200
        slot_id = r2.json()["id"]

        # Користувач бронює слот
        r3 = client.post("/api/bookings/", json={"slot_id": slot_id},
                         headers={"Authorization": f"Bearer {user_token}"})
        assert r3.status_code == 200
        assert r3.json()["status"] == "pending_payment"
        assert r3.json()["total_price"] == pytest.approx(600.0, rel=1e-3)

    def test_double_booking_fails(self, client, admin_token, user_token):
        r = client.post("/api/locations/", json={
            "name": "Корт Б", "category": "tennis",
            "address": "вул. 2", "price_per_hour": 200.0
        }, headers={"Authorization": f"Bearer {admin_token}"})
        location_id = r.json()["id"]

        from datetime import datetime, timezone, timedelta
        start = (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat()
        end = (datetime.now(timezone.utc) + timedelta(hours=7)).isoformat()
        r2 = client.post("/api/slots/", json={
            "location_id": location_id, "start_time": start, "end_time": end
        }, headers={"Authorization": f"Bearer {admin_token}"})
        slot_id = r2.json()["id"]

        client.post("/api/bookings/", json={"slot_id": slot_id},
                    headers={"Authorization": f"Bearer {user_token}"})
        r3 = client.post("/api/bookings/", json={"slot_id": slot_id},
                         headers={"Authorization": f"Bearer {user_token}"})
        assert r3.status_code == 400


# --- Scenario 3: Гість переглядає локації без реєстрації ---
class TestGuestAccess:
    def test_guest_can_view_locations(self, client, admin_token):
        client.post("/api/locations/", json={
            "name": "Басейн", "category": "pool",
            "address": "вул. 3", "price_per_hour": 500.0
        }, headers={"Authorization": f"Bearer {admin_token}"})

        r = client.get("/api/locations/")
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_guest_cannot_book(self, client, admin_token):
        r = client.post("/api/bookings/", json={"slot_id": 1})
        assert r.status_code == 403

    def test_guest_cannot_create_location(self, client):
        r = client.post("/api/locations/", json={
            "name": "Хак", "category": "gym",
            "address": "вул. Хакерська", "price_per_hour": 100.0
        })
        assert r.status_code == 403
