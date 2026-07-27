from pydantic import BaseModel
from typing import Optional


"""

Notice: Fields `id` and `created_at` will be automatically created at inserting row in a table.

"""


class Bookmark(BaseModel):
    url: str
    title: str
    description: str


class User(BaseModel):
    ...