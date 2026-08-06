from pydantic import BaseModel
from typing import Optional
from datetime import datetime


"""

Notice: Fields `id` and `created_at` will be automatically created at inserting row in a table.

"""


class Bookmark(BaseModel):
    id: Optional[int] = None
    url: str
    title: str
    description: str
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None

# Вход / Регистрация
class UserCreate(BaseModel):
    login: str
    password: str

# Ответ с данными пользователя
class UserOut(BaseModel):
    id: int
    login: str
    created_at: datetime

# Ответ при успехе аутентификации
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"