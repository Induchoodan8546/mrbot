
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.conversations import router as conversations_router
from app.core.config import settings
from app.core.exception_handlers import (
    unexpected_exception_handler,
    validation_exception_handler,
)
from app.core.logging_config import configure_logging
from app.infrastructure.database.connection import init_db


configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MRBot application starting")

    try:
        init_db()
        logger.info("Database initialization completed")
    except Exception:
        logger.exception("Database initialization failed")
        raise

    try:
        yield
    finally:
        logger.info("MRBot application shutting down")


app = FastAPI(
    title=settings.app_name,
    description="Production-oriented local AI chatbot",
    version=settings.app_version,
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception:
        logger.exception(
            "Request processing failed: %s %s",
            request.method,
            request.url.path,
        )
        raise
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "HTTP %s %s | status=%s | duration_ms=%.2f",
            request.method,
            request.url.path,
            status_code,
            duration_ms,
        )


app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    unexpected_exception_handler,
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(conversations_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} API is running"
    }
