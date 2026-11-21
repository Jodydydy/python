from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """Модель пользователя с базовыми полями"""
    username: str
    full_name: str | None = None
    email: EmailStr | None = None
    disabled: bool = False
    roles: list[str]  # Список ролей пользователя

class UserLogin(BaseModel):
    """Модель для входа в систему"""
    username: str
    password: str
