# SportBook UA — Система бронювання спортивних локацій

[![CI/CD](https://github.com/DariiaTar/refactoring_project2/actions/workflows/ci.yml/badge.svg)](https://github.com/DariiaTar/refactoring_project2/actions/workflows/ci.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=dariiatar_refactoring_project2&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=dariiatar_refactoring_project2)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=dariiatar_refactoring_project2&metric=coverage)](https://sonarcloud.io/summary/new_code?id=dariiatar_refactoring_project2)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=dariiatar_refactoring_project2&metric=bugs)](https://sonarcloud.io/summary/new_code?id=dariiatar_refactoring_project2)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=dariiatar_refactoring_project2&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=dariiatar_refactoring_project2)

Повнофункціональна система для бронювання спортивних локацій: тенісні корти, футбольні поля, басейни, тренажерні зали.

**Backend:** Python 3.11, FastAPI, SQLAlchemy, PostgreSQL, JWT  
**Frontend:** React 18, React Router, Axios  
**DevOps:** Docker, Docker Compose, GitHub Actions CI/CD

---

## Якість коду (SonarCloud)

| Метрика | Значення |
|---------|----------|
| Тести | **352** (344 unit + 8 integration) |
| Покриття | **≥ 80%** |
| Bugs | **0** |
| Code Smells | **A** |
| Duplications | **< 3%** |

Повний звіт: [SonarCloud Dashboard](https://sonarcloud.io/summary/new_code?id=dariiatar_refactoring_project2)

---

## Архітектура

Layered (шарова) архітектура зі строгим напрямком залежностей:

```
[HTTP Request]
      ↓
[Controllers]  — приймають запит, повертають відповідь
      ↓
[Services]     — бізнес-логіка, GoF патерни (Strategy, Observer)
      ↓
[Repositories] — абстракції (Interface) + SQL/In-Memory реалізації
      ↓
[Models]       — SQLAlchemy ORM, сутності домену
```

Принципи SOLID:
- **S** — кожен клас має одну відповідальність
- **O** — нова поведінка через Strategy/Observer injection
- **L** — InMemory репозиторії є drop-in заміною SQL
- **I** — ABC інтерфейси дрібні й сфокусовані
- **D** — сервіси залежать від `IRepository`, не від конкретних класів

## Ролі користувачів

| Роль | Права |
|------|-------|
| Гість | Перегляд локацій та слотів |
| Користувач | Реєстрація, бронювання, оплата, скасування своїх броней |
| Адмін | Повне управління: локації, слоти, бронювання, користувачі |

---

## Швидкий старт

### Запуск через Docker Compose (рекомендовано)

```bash
# 1. Клонувати репозиторій
git clone <repo-url>
cd sport-booking

# 2. Налаштувати змінні середовища
cp .env.example .env
# Відредагуйте .env — обов'язково змініть SECRET_KEY

# 3. Запустити всі сервіси
docker compose up --build -d

# 4. Застосувати міграції
docker compose exec backend alembic upgrade head

# 5. Заповнити тестовими даними (опціонально)
docker compose exec backend python db/seed/seed.py
```

Після запуску:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

### Тестові акаунти (після seed)

```
Admin:  admin@sportbook.ua / admin123
User:   ivan@example.com  / user123
```

### Локальний запуск (розробка)

**Backend:**
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # відредагуйте DATABASE_URL
uvicorn src.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

---

## Змінні середовища та секрети

Усі конфіденційні параметри зберігаються у файлі `.env`, який **не комітиться у git**.

| Змінна | Призначення | Приклад |
|--------|-------------|---------|
| `DATABASE_URL` | Рядок підключення до PostgreSQL | `postgresql://user:pass@host/db` |
| `SECRET_KEY` | Підпис JWT-токенів (мін. 32 символи) | `$(python -c "import secrets; print(secrets.token_hex(32))")` |
| `POSTGRES_USER` | Логін PostgreSQL (тільки для docker-compose) | `sportbook` |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL | сильний пароль |
| `POSTGRES_DB` | Назва бази даних | `sportbook` |

**Правила безпеки:**
- `.env` завжди в `.gitignore`
- У CI/CD секрети зберігаються у GitHub Secrets (Settings → Secrets and variables)
- Для продакшну генеруйте `SECRET_KEY` командою: `python -c "import secrets; print(secrets.token_hex(32))"`
- Ніколи не передавайте реальні паролі у `docker-compose.yml` — тільки через `${VAR}` з `.env`

---

## Запуск тестів

```bash
# Всі тести (352 total: 344 unit + 8 integration)
pytest

# Тільки юніт-тести
pytest tests/unit/ -v

# Тільки інтеграційні
pytest tests/integration/ -v

# З покриттям коду (HTML + XML для SonarCloud)
SECRET_KEY=test-secret-key pytest tests/unit/ \
  --cov=src --cov-report=html:htmlcov \
  --cov-report=xml:coverage.xml \
  --junitxml=junit.xml
# HTML звіт: htmlcov/index.html
```

---

## API Endpoints

| Метод | URL | Опис | Доступ |
|-------|-----|------|--------|
| POST | `/api/auth/register` | Реєстрація | Всі |
| POST | `/api/auth/login` | Вхід | Всі |
| GET | `/api/auth/me` | Профіль | Авторизований |
| GET | `/api/locations/` | Список локацій | Всі |
| GET | `/api/locations/{id}` | Деталі локації | Всі |
| POST | `/api/locations/` | Створити локацію | Адмін |
| PUT | `/api/locations/{id}` | Оновити локацію | Адмін |
| DELETE | `/api/locations/{id}` | Видалити локацію | Адмін |
| POST | `/api/locations/{id}/images` | Завантажити фото | Адмін |
| GET | `/api/slots/location/{id}/available` | Доступні слоти | Всі |
| POST | `/api/slots/` | Створити слот | Адмін |
| DELETE | `/api/slots/{id}` | Видалити слот | Адмін |
| POST | `/api/bookings/` | Забронювати | Авторизований |
| GET | `/api/bookings/my` | Мої бронювання | Авторизований |
| GET | `/api/bookings/{id}` | Деталі бронювання | Авторизований / Адмін |
| POST | `/api/bookings/{id}/pay` | Оплатити | Авторизований |
| POST | `/api/bookings/{id}/cancel` | Скасувати | Авторизований |
| GET | `/api/bookings/` | Всі бронювання | Адмін |
| PUT | `/api/bookings/{id}/status` | Змінити статус | Адмін |
| GET | `/api/users/` | Список користувачів | Адмін |
| PUT | `/api/users/{id}/deactivate` | Заблокувати | Адмін |

Інтерактивна документація: http://localhost:8000/docs

---

## Управління гілками (Branching Strategy)

Проєкт використовує спрощений **Git Flow**:

```
main        ← стабільний продакшн-код (захищена гілка)
develop     ← інтеграційна гілка для нових фіч
feature/*   ← розробка нових функцій
fix/*       ← виправлення багів
```

### Правила роботи з гілками

```bash
# 1. Нова фіча — завжди від develop
git checkout develop
git pull origin develop
git checkout -b feature/booking-payment

# 2. Після завершення — PR у develop
git push origin feature/booking-payment
# Відкрийте Pull Request: feature/booking-payment → develop

# 3. Після тестування на develop — PR у main
# Відкрийте Pull Request: develop → main

# 4. Після мержу в main — CI автоматично білдить Docker образи
```

### Захист гілок (Branch Protection)

Налаштовано у **GitHub → Settings → Branches → Add rule** для `main`:
- ✅ Require status checks to pass before merging
  - `Unit Tests (Backend)`, `Integration Tests (Backend)`, `Code Style (flake8)`, `Frontend Build`
- ✅ Require branches to be up to date before merging
- ✅ Do not allow bypassing the above settings

Merge заблоковано, якщо CI "червоний" або Quality Gate провалено.

### Іменування комітів

```
feat: додати оплату бронювання
fix: виправити валідацію телефону
refactor: розбити BookingService на менші методи
test: додати тести для LocationService
docs: оновити README з інструкціями розгортання
ci: додати кешування pip у GitHub Actions
```

---

## CI/CD Pipeline

GitHub Actions запускається автоматично при кожному push:

```
push to any branch
    │
    ├─→ Unit Tests (з coverage)
    ├─→ Integration Tests (PostgreSQL service)
    ├─→ Lint (flake8)
    └─→ Frontend Build
            │
            └─→ (тільки main) Docker Build
                        │
                        └─→ (розкоментувати) Deploy to Production
```

**Секрети для CI/CD** (додати у GitHub → Settings → Secrets):

| Secret | Призначення |
|--------|-------------|
| `SECRET_KEY` | JWT підпис (продакшн) |
| `DEPLOY_HOST` | IP/hostname продакшн-сервера |
| `DEPLOY_USER` | SSH-логін |
| `DEPLOY_SSH_KEY` | Приватний SSH-ключ для деплою |

---

## Багатоконтейнерна система (Multi-Container)

### Архітектура контейнерів

```
┌─────────────────────────────────────────────┐
│               sportbook-net                 │
│                                             │
│  ┌──────────┐   ┌──────────┐   ┌────────┐  │
│  │ frontend │──→│ backend  │──→│   db   │  │
│  │ :3000/80 │   │  :8000   │   │  :5432 │  │
│  └──────────┘   └──────────┘   └────────┘  │
│                      │                      │
│               uploads_data (volume)         │
└─────────────────────────────────────────────┘
```

### Корисні команди

```bash
# Запустити всі сервіси у фоні
docker compose up -d

# Переглянути логи
docker compose logs -f backend
docker compose logs -f db

# Зайти в контейнер
docker compose exec backend bash
docker compose exec db psql -U sportbook -d sportbook

# Застосувати міграції
docker compose exec backend alembic upgrade head

# Перезібрати тільки backend після змін
docker compose up -d --build backend

# Зупинити всі сервіси
docker compose down

# Повне очищення (включно з volumes — УВАГА: видаляє дані)
docker compose down -v
```

### Best Practices мультиконтейнерної системи

1. **Іменована мережа** (`sportbook-net`) — сервіси спілкуються по імені, не по IP
2. **Named volumes** (`postgres_data`, `uploads_data`) — дані живуть поза контейнером; перезапуск не знищує БД
3. **Healthcheck** — `backend` стартує тільки після готовності `db`; `frontend` — після `backend`
4. **`unless-stopped`** — контейнери автоматично рестартують після збою або перезавантаження сервера
5. **`.dockerignore`** — виключає `node_modules`, `.env`, `__pycache__` з контексту збірки
6. **Секрети через env_file** — `.env` не потрапляє в образ, передається тільки в runtime
7. **Multi-stage build** (frontend) — `node:alpine` для збірки → `nginx:alpine` для serve; образ менший у 10+ разів

---

## Бізнес-логіка та алгоритми

### Алгоритми розрахунку ціни (GoF Strategy)

| Стратегія | Умова | Розрахунок |
|-----------|-------|-----------|
| `StandardPricingStrategy` | За замовчуванням | `ціна/год × кількість годин` |
| `PeakHourPricingStrategy` | Початок бронювання 18:00–22:00 | `базова × 1.25` (+25%) |
| `WeekendPricingStrategy` | Субота або неділя | `базова × 1.50` (+50%) |

Стратегія переключається через `DynamicPricingContext.set_strategy()` без зміни коду сервісу.

### Lifecycle бронювання

```
[Слот: AVAILABLE]
       ↓ create_booking()
[Booking: PENDING_PAYMENT] ← слот стає BOOKED
       ↓ pay_booking()            ↓ cancel_booking()
[Booking: CONFIRMED]      [Booking: CANCELLED] → слот знову AVAILABLE
```

### Сповіщення про події (GoF Observer)

`BookingNotifier` сповіщує всіх підписників (`LoggingObserver`, `EmailNotificationObserver`) при:
- `on_booking_created` — бронювання створено
- `on_booking_confirmed` — оплачено
- `on_booking_cancelled` — скасовано

Нові спостерігачі підключаються через `BookingService.add_observer()` без зміни логіки.

---

## Design Patterns

| Патерн | Реалізація |
|--------|-----------|
| **Strategy** (GoF) | `IPricingStrategy` → `StandardPricingStrategy`, `PeakHourPricingStrategy`, `WeekendPricingStrategy` — розрахунок ціни бронювання |
| **Observer** (GoF) | `IBookingObserver` → `LoggingObserver`, `EmailNotificationObserver`; `BookingNotifier` повідомляє підписників про події бронювання |
| **Repository** (GoF) | `IBookingRepository`, `IUserRepository` тощо — ізоляція SQL від бізнес-логіки; `InMemory*` реалізації для тестів |
| **Singleton** (GoF) | `AppSettings.get_instance()` у `src/config/settings.py` |
| **DTO** | Pydantic-схеми між шарами: `BookingCreateDTO`, `BookingDetailsResponseDTO` |
| **Dependency Injection** | FastAPI `Depends(get_db)`, `Depends(get_current_user)` |

---

## Структура репозиторію

```
sport-booking/
├── src/
│   ├── controllers/         HTTP handlers (FastAPI routers)
│   ├── services/
│   │   ├── booking_service.py      Бізнес-логіка бронювань
│   │   ├── pricing_strategy.py     GoF Strategy: 3 цінових стратегії
│   │   ├── booking_observer.py     GoF Observer: сповіщення про події
│   │   ├── auth_service.py         JWT автентифікація
│   │   └── location_service.py     Управління локаціями
│   ├── repositories/
│   │   ├── interfaces.py           ABC: IUserRepo, ILocationRepo, ISlotRepo, IBookingRepo
│   │   ├── in_memory.py            In-Memory реалізації для тестів
│   │   ├── user_repository.py      SQL реалізація
│   │   ├── location_repository.py
│   │   ├── slot_repository.py
│   │   └── booking_repository.py
│   ├── models/              SQLAlchemy ORM (User, Location, Slot, Booking)
│   ├── dto/                 Pydantic схеми вхід/вихід
│   ├── config/              database.py, settings.py (Singleton), dependencies.py
│   └── main.py              FastAPI app + CORS + routers
├── tests/
│   ├── unit/                344 юніт-тести (mock-based + in-memory)
│   │   ├── test_booking_service.py
│   │   ├── test_pricing_strategy.py   GoF Strategy тести (50+)
│   │   ├── test_observer.py           GoF Observer тести (45+)
│   │   ├── test_in_memory_repositories.py  In-Memory тести (70+)
│   │   ├── test_repositories.py       Mock DB тести
│   │   ├── test_auth_service.py
│   │   ├── test_location_service.py
│   │   ├── test_models.py
│   │   ├── test_dto_validation.py
│   │   └── test_price_calculation.py
│   └── integration/         8 інтеграційних тестів (TestClient + SQLite)
├── docs/
│   ├── diagrams/            UML діаграми (Mermaid)
│   │   ├── use_case.md
│   │   ├── domain_model.md
│   │   └── class_diagram.md
│   └── spec/api_spec.md     REST API специфікація
├── .cursor/rules/           AI контекст для Cursor/Claude
│   ├── architecture.md
│   └── testing_strategy.md
├── .github/workflows/
│   └── ci.yml               GitHub Actions: test → lint → sonar → docker
├── .cursorrules             Глобальні правила для AI-агентів
├── sonar-project.properties SonarCloud конфігурація
├── .coveragerc              Coverage.py налаштування (relative_files)
├── Dockerfile               Backend image
├── docker-compose.yml       Multi-container setup
├── .env.example             Шаблон змінних середовища
└── requirements.txt         Python залежності
```
