from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description="Production-oriented local AI chatbot",
    version=settings.app_version,
)


app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    chat_router,
    prefix="/api/v1",
)


@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} API is running"
    }