from dotenv import load_dotenv
from os import getenv, path, listdir
import asyncpg
from logging import info, error
from .models import Bookmark, UserOut
import asyncio


load_dotenv()
DSN_LINK = getenv("PG_LINK")

class Database:

    _conn = None

    @classmethod
    async def initialize(cls) -> None:
        if cls._conn is None:
            cls._conn = await asyncpg.connect(dsn=DSN_LINK)
            if path.exists("database/schemas"):
                for i in listdir("database/schemas"):
                    with open(f"database/schemas/{i}") as f:
                        sql = f.read()
                        await cls._conn.execute(sql)
                info("DB initialized")
            else:
                error("Missing schemas dir. Can not initial DB")


    @classmethod
    async def create_user(cls, login: str, password_hash: str) -> UserOut | None:
        if cls._conn:
            row = await cls._conn.fetchrow(
                """INSERT INTO users (login, password_hash)
                   VALUES ($1, $2)
                   RETURNING id, login, created_at""",
                login, password_hash
            )
            if row:
                return UserOut(**dict(row))
        return None


    @classmethod
    async def get_user_by_login(cls, login: str) -> dict | None:
        if cls._conn:
            row = await cls._conn.fetchrow(
                """SELECT id, login, password_hash, created_at FROM users WHERE login = $1""",
                login
            )
            if row:
                return dict(row)
        return None


    @classmethod
    async def get_user_by_id(cls, user_id: int) -> UserOut | None:
        if cls._conn:
            row = await cls._conn.fetchrow(
                """SELECT id, login, created_at FROM users WHERE id = $1""",
                user_id
            )
            if row:
                return UserOut(**dict(row))
        return None


    @classmethod
    async def add_bookmark(cls, bookmark: Bookmark, user_id: int) -> bool:
        if cls._conn is not None:
            res = await cls._conn.execute(
                """INSERT INTO bookmarks (url, title, description, user_id)
                VALUES ($1, $2, $3, $4)""",
                bookmark.url, bookmark.title, bookmark.description, user_id)
            return bool(res)
        return False


    @classmethod
    async def get_bookmarks(cls, user_id: int) -> list[Bookmark]:
        if cls._conn is not None:
            res = await cls._conn.fetch(
                """SELECT * FROM bookmarks WHERE user_id = $1""", user_id
            )
            return [Bookmark(**record) for record in res]
        return []


    @classmethod
    async def delete_bookmark(cls, id: int, user_id: int) -> bool:
        if cls._conn is not None:
            res = await cls._conn.execute(
                """DELETE FROM bookmarks WHERE id = $1 AND user_id = $2""", id, user_id
            )
            return res == "DELETE 1"
        return False
    

    @classmethod
    async def close_all(cls):
        """Закрывает пул соединений. Вызывается при остановке приложения."""
        if cls._conn:
            await cls._conn.close()
            cls._conn = None
            info("Соединение закрыто.")


if __name__ == "__main__":
    async def test():
        conn = await asyncpg.connect(dsn=DSN_LINK)
        with open("schemas/bookmarks.sql") as f:
            sql = f.read()
            res = await conn.execute(sql)
            return res

    asyncio.run(test())
    