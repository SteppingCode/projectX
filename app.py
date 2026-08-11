import jwt

from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from database.database import Database
from database.models import *

from auth import hash_password, verify_password, create_access_token, get_current_user, create_refresh_token
from auth import SECRET_KEY, ALGORITHM

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


@router.post("/auth/register", response_model=UserOut)
async def register(
    user_data: UserCreate
):
    existing_user = await Database.get_user_by_login(user_data.login)
    if existing_user:
        raise HTTPException(status_code=400, detail="Логин уже занят")
    
    hashed_pwd = hash_password(user_data.password)
    new_user = await Database.create_user(user_data.login, hashed_pwd)
    return new_user


@router.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await Database.get_user_by_login(form_data.username)
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user["id"])})
    refresh_token = create_refresh_token(data={"sub": str(user["id"])})
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer"
    }


@router.post("/auth/refresh", response_model=Token)
async def refresh(
    body: TokenRefresh
):
    """Обмен refresh токена на новую пару access/refresh токенов."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный или просроченный refresh токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(body.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise credentials_exception
            
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
            
    except jwt.ExpiredSignatureError:
        # Если истек и Refresh-токен — пользователю придется войти заново
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = await Database.get_user_by_id(int(user_id_str))
    if user is None:
        raise credentials_exception

    new_access_token = create_access_token(data={"sub": user_id_str})
    new_refresh_token = create_refresh_token(data={"sub": user_id_str})
    
    return {
        "access_token": new_access_token, 
        "refresh_token": new_refresh_token, 
        "token_type": "bearer"
    }


@router.get("/")
async def api_status():
    return "API is working. Use /api/docs for API documentation"


@router.post("/add_bookmark/", response_model=bool)
async def add_bookmark_to_db(
    url: str, 
    current_user: UserOut = Depends(get_current_user)
):
    metadata = await fetch_url_metadata(url)

    bookmark = Bookmark(
        url=url,
        title=metadata["title"],
        description=metadata["description"]
    )
    
    return await Database.add_bookmark(bookmark, user_id=current_user.id)


@router.get("/bookmarks", response_model=List[Bookmark])
async def get_all_bookmarks(
    current_user: UserOut = Depends(get_current_user)
):
    return await Database.get_bookmarks(user_id=current_user.id)


@router.delete("/delete_bookmark/{id}", response_model=bool)
async def delete_bookmark_by_id(
    id: int, 
    current_user: UserOut = Depends(get_current_user)
):
    return await Database.delete_bookmark(id, user_id=current_user.id)


app.include_router(router)