from fastapi import FastAPI

from app.api.routes.health import router as health_router


app = FastAPI(
    title="MRBot",
    description="Production-oriented local AI chatbot",
    version="0.1.0",
)


app.include_router(
    health_router,
    prefix="/api/v1",
)


@app.get("/")
def root():
    return {"message": "MRBot API is running"}