from fastapi import APIRouter, FastAPI
from fastapi.responses import RedirectResponse
from database.database import Database
from database.models import *
from contextlib import asynccontextmanager
from typing import List
from parser import fetch_url_metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализируем БД при старте
    await Database.initialize()
    yield
    await Database.close_all()


app = FastAPI(
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    title="Bookmarks API",
    description="API for managing bookmarks",
    version="0.0.1"
    )
router = APIRouter(prefix="/api")


@app.get("/")
async def redirect_to_api():
    return RedirectResponse("/api", status_code=302)


@router.get("/")
async def status():
    return "API is working. Use /api/docs for API documentation"


@router.post("/add_url/", response_model=bool)
async def add_url_to_db(url: str):
    metadata = await fetch_url_metadata(url)

    bookmark = Bookmark(
        url=url,
        title=metadata["title"],
        description=metadata["description"]
    )
    
    return await Database.add_bookmark(bookmark)


@router.get("/urls", response_model=List[Bookmark])
async def get_all_urls():
    return await Database.get_urls()


@router.delete("/delete_url/{id}", response_model=bool)
async def delete_url_by_id(id: int):
    return await Database.delete_url(id)


app.include_router(router)