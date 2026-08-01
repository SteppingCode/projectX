from pydantic import BaseModel
from typing import Optional
from datetime import datetime


"""

Notice: Fields `id` and `created_at` will be automatically created at inserting row in a table.

"""


class Bookmark(BaseModel):
    id: Optional[int] = None
    url: str
    title: str        # Убрали Optional и дефолтные значения
    description: str  # Теперь модель строго требует эти данные
    created_at: Optional[datetime] = datetime.now()


class User(BaseModel):
    ...