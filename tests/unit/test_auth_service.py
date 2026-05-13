import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from datetime import datetime, timezone

from src.services.auth_service import AuthService
from src.models.user import User, UserRole
from src.dto.user_dto import UserRegisterDTO, UserLoginDTO


def make_user(role=UserRole.USER, is_active=True, email="test@example.com"):
    user = User()
    user.id = 1
    user.email = email
    user.full_name = "Тест Юзер"
    user.hashed_password = "$2b$12$fakehashedpassword"
    user.role = role
    user.is_active = is_active
    user.phone = None
    user.created_at = datetime.now(timezone.utc)
    return user


@pytest.fixture
def auth_service():
    db = MagicMock()
    return AuthService(db)


class TestHashPassword:
    def test_hash_is_not_plaintext(self, auth_service):
        result = auth_service.hash_password("secret123")
        assert result != "secret123"

    def test_hash_is_string(self, auth_service):
        result = auth_service.hash_password("password")
        assert isinstance(result, str)

    def test_different_passwords_different_hashes(self, auth_service):
        h1 = auth_service.hash_password("pass1")
        h2 = auth_service.hash_password("pass2")
        assert h1 != h2

    def test_same_password_different_hashes_each_time(self, auth_service):
        h1 = auth_service.hash_password("samepass")
        h2 = auth_service.hash_password("samepass")
        assert h1 != h2

    def test_hash_starts_with_bcrypt_prefix(self, auth_service):
        result = auth_service.hash_password("mypass")
        assert result.startswith("$2b$")

    def test_hash_long_password(self, auth_service):
        long_pass = "a" * 100
        result = auth_service.hash_password(long_pass)
        assert isinstance(result, str)

    def test_hash_special_characters(self, auth_service):
        result = auth_service.hash_password("p@$$w0rd!#%^&*()")
        assert result != "p@$$w0rd!#%^&*()"

    def test_hash_unicode_password(self, auth_service):
        result = auth_service.hash_password("пароль123")
        assert isinstance(result, str)


class TestVerifyPassword:
    def test_correct_password_returns_true(self, auth_service):
        hashed = auth_service.hash_password("mypassword")
        assert auth_service.verify_password("mypassword", hashed) is True

    def test_wrong_password_returns_false(self, auth_service):
        hashed = auth_service.hash_password("mypassword")
        assert auth_service.verify_password("wrongpassword", hashed) is False

    def test_empty_password_returns_false(self, auth_service):
        hashed = auth_service.hash_password("mypassword")
        assert auth_service.verify_password("", hashed) is False

    def test_case_sensitive_password(self, auth_service):
        hashed = auth_service.hash_password("Password")
        assert auth_service.verify_password("password", hashed) is False

    def test_whitespace_matters(self, auth_service):
        hashed = auth_service.hash_password("pass word")
        assert auth_service.verify_password("password", hashed) is False

    def test_verify_special_chars(self, auth_service):
        hashed = auth_service.hash_password("p@$$w0rd!")
        assert auth_service.verify_password("p@$$w0rd!", hashed) is True


class TestCreateToken:
    def test_returns_string(self, auth_service):
        token = auth_service.create_access_token(1, "user")
        assert isinstance(token, str)

    def test_decode_valid_token(self, auth_service):
        token = auth_service.create_access_token(42, "admin")
        payload = auth_service.decode_token(token)
        assert payload["sub"] == "42"
        assert payload["role"] == "admin"

    def test_invalid_token_raises(self, auth_service):
        with pytest.raises(HTTPException) as exc:
            auth_service.decode_token("invalidtoken")
        assert exc.value.status_code == 401

    def test_token_contains_expiry(self, auth_service):
        token = auth_service.create_access_token(1, "user")
        payload = auth_service.decode_token(token)
        assert "exp" in payload

    def test_token_sub_is_string(self, auth_service):
        token = auth_service.create_access_token(99, "user")
        payload = auth_service.decode_token(token)
        assert payload["sub"] == "99"

    def test_admin_role_in_token(self, auth_service):
        token = auth_service.create_access_token(1, "admin")
        payload = auth_service.decode_token(token)
        assert payload["role"] == "admin"

    def test_tampered_token_raises(self, auth_service):
        token = auth_service.create_access_token(1, "user")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(HTTPException) as exc:
            auth_service.decode_token(tampered)
        assert exc.value.status_code == 401

    def test_empty_token_raises(self, auth_service):
        with pytest.raises(HTTPException) as exc:
            auth_service.decode_token("")
        assert exc.value.status_code == 401

    def test_different_user_ids_different_tokens(self, auth_service):
        t1 = auth_service.create_access_token(1, "user")
        t2 = auth_service.create_access_token(2, "user")
        assert t1 != t2


class TestRegister:
    def test_register_success(self, auth_service):
        auth_service.user_repo.get_by_email = MagicMock(return_value=None)
        new_user = make_user()
        auth_service.user_repo.create = MagicMock(return_value=new_user)

        data = UserRegisterDTO(email="new@example.com", full_name="Новий Юзер", password="pass123")  # NOSONAR
        result = auth_service.register(data)
        assert result.access_token is not None

    def test_register_duplicate_email_raises(self, auth_service):
        auth_service.user_repo.get_by_email = MagicMock(return_value=make_user())
        data = UserRegisterDTO(email="existing@example.com", full_name="Існуючий", password="pass123")  # NOSONAR
        with pytest.raises(HTTPException) as exc:
            auth_service.register(data)
        assert exc.value.status_code == 400

    def test_register_returns_token_dto(self, auth_service):
        auth_service.user_repo.get_by_email = MagicMock(return_value=None)
        auth_service.user_repo.create = MagicMock(return_value=make_user())
        data = UserRegisterDTO(email="new@example.com", full_name="Новий", password="pass123")  # NOSONAR
        result = auth_service.register(data)
        assert hasattr(result, "access_token")
        assert hasattr(result, "user")

    def test_register_password_is_hashed(self, auth_service):
        auth_service.user_repo.get_by_email = MagicMock(return_value=None)
        auth_service.user_repo.create = MagicMock(return_value=make_user())
        data = UserRegisterDTO(email="new@example.com", full_name="Новий", password="plainpass")  # NOSONAR
        auth_service.register(data)
        call_kwargs = auth_service.user_repo.create.call_args[1]
        assert call_kwargs["hashed_password"] != "plainpass"

    def test_register_calls_repo_create(self, auth_service):
        auth_service.user_repo.get_by_email = MagicMock(return_value=None)
        auth_service.user_repo.create = MagicMock(return_value=make_user())
        data = UserRegisterDTO(email="new@example.com", full_name="Новий", password="pass123")  # NOSONAR
        auth_service.register(data)
        auth_service.user_repo.create.assert_called_once()

    def test_register_with_phone(self, auth_service):
        auth_service.user_repo.get_by_email = MagicMock(return_value=None)
        user = make_user()
        user.phone = "+380501234567"
        auth_service.user_repo.create = MagicMock(return_value=user)
        data = UserRegisterDTO(
            email="new@example.com", full_name="Новий", password="pass123", phone="+380501234567"  # NOSONAR
        )
        result = auth_service.register(data)
        assert result.user.phone == "+380501234567"

    def test_register_error_message_contains_email(self, auth_service):
        auth_service.user_repo.get_by_email = MagicMock(return_value=make_user())
        data = UserRegisterDTO(email="dup@example.com", full_name="Юзер", password="pass123")  # NOSONAR
        with pytest.raises(HTTPException) as exc:
            auth_service.register(data)
        assert "email" in exc.value.detail.lower() or "існує" in exc.value.detail.lower()


class TestLogin:
    def test_login_success(self, auth_service):
        user = make_user()
        user.hashed_password = auth_service.hash_password("correct_password")
        auth_service.user_repo.get_by_email = MagicMock(return_value=user)

        data = UserLoginDTO(email="test@example.com", password="correct_password")  # NOSONAR
        result = auth_service.login(data)
        assert result.access_token is not None

    def test_login_wrong_password_raises(self, auth_service):
        user = make_user()
        user.hashed_password = auth_service.hash_password("correct_password")
        auth_service.user_repo.get_by_email = MagicMock(return_value=user)

        data = UserLoginDTO(email="test@example.com", password="wrong_password")  # NOSONAR
        with pytest.raises(HTTPException) as exc:
            auth_service.login(data)
        assert exc.value.status_code == 401

    def test_login_nonexistent_user_raises(self, auth_service):
        auth_service.user_repo.get_by_email = MagicMock(return_value=None)
        data = UserLoginDTO(email="nobody@example.com", password="pass123")  # NOSONAR
        with pytest.raises(HTTPException) as exc:
            auth_service.login(data)
        assert exc.value.status_code == 401

    def test_login_inactive_user_raises(self, auth_service):
        user = make_user(is_active=False)
        user.hashed_password = auth_service.hash_password("pass123")
        auth_service.user_repo.get_by_email = MagicMock(return_value=user)

        data = UserLoginDTO(email="test@example.com", password="pass123")  # NOSONAR
        with pytest.raises(HTTPException) as exc:
            auth_service.login(data)
        assert exc.value.status_code == 403

    def test_login_returns_user_data(self, auth_service):
        user = make_user()
        user.hashed_password = auth_service.hash_password("pass123")
        auth_service.user_repo.get_by_email = MagicMock(return_value=user)
        data = UserLoginDTO(email="test@example.com", password="pass123")  # NOSONAR
        result = auth_service.login(data)
        assert result.user.email == "test@example.com"

    def test_login_token_contains_correct_role(self, auth_service):
        user = make_user(role=UserRole.ADMIN)
        user.hashed_password = auth_service.hash_password("pass123")
        auth_service.user_repo.get_by_email = MagicMock(return_value=user)
        data = UserLoginDTO(email="test@example.com", password="pass123")  # NOSONAR
        result = auth_service.login(data)
        payload = auth_service.decode_token(result.access_token)
        assert payload["role"] == UserRole.ADMIN

    def test_login_empty_password_raises(self, auth_service):
        user = make_user()
        user.hashed_password = auth_service.hash_password("pass123")
        auth_service.user_repo.get_by_email = MagicMock(return_value=user)
        data = UserLoginDTO(email="test@example.com", password="")  # NOSONAR
        with pytest.raises(HTTPException) as exc:
            auth_service.login(data)
        assert exc.value.status_code == 401

    def test_login_inactive_403_not_401(self, auth_service):
        user = make_user(is_active=False)
        user.hashed_password = auth_service.hash_password("pass123")  # NOSONAR
        auth_service.user_repo.get_by_email = MagicMock(return_value=user)
        data = UserLoginDTO(email="test@example.com", password="pass123")  # NOSONAR
        with pytest.raises(HTTPException) as exc:
            auth_service.login(data)
        assert exc.value.status_code != 401
        assert exc.value.status_code == 403
