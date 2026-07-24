from fastapi import APIRouter, FastAPI
from fastapi.responses import RedirectResponse


app = FastAPI()
router = APIRouter(prefix="/api")


@app.get("/")
async def redirect_to_api():
    """
    Just redirect to '/api' url
    """
    return RedirectResponse("/api")


@router.get("/")
async def root():
    return "Hello World!"


app.include_router(router)