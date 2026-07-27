from dotenv import load_dotenv
from os import getenv, path, listdir
import asyncpg
from logging import info, error
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
    async def add_bookmark(cls, url: str) -> bool | None:
        if cls._conn is not None:
            res = await cls._conn.execute(
                """INSERT INTO bookmarks (url, title, description)
                VALUES ($1, 'title', 'desc')""",
                url)
            if res:
                return True
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
    