import jwt, bcrypt
from datetime import datetime, timedelta, timezone
from os import getenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database.database import Database
from database.models import UserOut

SECRET_KEY = getenv("SECRET_KEY", "super-secret-key-change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15 
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    """Хэширует пароль с использованием bcrypt."""
    salt = bcrypt.gensalt()
    pwd_bytes = password.encode('utf-8')
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль на соответствие хэшу."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict) -> str:
    """Создает подписсанный Access JWT токен с меткой типа."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Создает долгоживущий Refresh токен с меткой типа."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "access":
            raise credentials_exception
            
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        
        user_id = int(user_id_str) 
        
    except jwt.ExpiredSignatureError:
        # Сигнал для клиента: Access-токен просрочен, пора вызывать /auth/refresh
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception

    user = await Database.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user