from fastapi import APIRouter, FastAPI
from fastapi.responses import RedirectResponse
from database.database import Database
from database.models import *
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализируем БД при старте
    await Database.initialize()
    yield
    await Database.close_all()


app = FastAPI(lifespan=lifespan)
router = APIRouter(prefix="/api")


@app.get("/")
async def redirect_to_api():
    """
    Just redirect to '/api' url
    """
    return RedirectResponse("/api", status_code=302)


@router.get("/")
async def root():
    return "Hello World!"


@router.get("/add_url/{url}")
async def add_url_to_db(url: str):
    return await Database.add_bookmark(url)


app.include_router(router)