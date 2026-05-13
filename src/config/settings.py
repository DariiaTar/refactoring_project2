import os
import secrets
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY: str = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


class AppSettings:
    """Singleton — єдиний екземпляр налаштувань застосунку (GoF Singleton).

    Гарантує, що конфігурація зчитується з оточення лише один раз
    і доступна через AppSettings.get_instance() будь-де в коді.
    """

    _instance: "AppSettings | None" = None

    def __init__(self) -> None:
        self.secret_key: str = SECRET_KEY
        self.algorithm: str = ALGORITHM
        self.token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
        self.upload_dir: str = UPLOAD_DIR
        self.max_file_size: int = MAX_FILE_SIZE
        self.allowed_image_types: set = ALLOWED_IMAGE_TYPES

    @classmethod
    def get_instance(cls) -> "AppSettings":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
