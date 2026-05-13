from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from src.repositories.user_repository import UserRepository
from src.dto.user_dto import UserRegisterDTO, UserLoginDTO, TokenDTO, UserResponseDTO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, user_id: int, role: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {"sub": str(user_id), "role": role, "exp": expire}
        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалідний або прострочений токен",
            )

    def register(self, data: UserRegisterDTO) -> TokenDTO:
        if self.user_repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Користувач з таким email вже існує",
            )
        hashed = self.hash_password(data.password)
        user = self.user_repo.create(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hashed,
            phone=data.phone,
        )
        token = self.create_access_token(user.id, user.role)
        return TokenDTO(access_token=token, user=UserResponseDTO.from_orm(user))

    def login(self, data: UserLoginDTO) -> TokenDTO:
        user = self.user_repo.get_by_email(data.email)
        if not user or not self.verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний email або пароль",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Акаунт заблоковано",
            )
        token = self.create_access_token(user.id, user.role)
        return TokenDTO(access_token=token, user=UserResponseDTO.from_orm(user))
