from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.tasks import router as tasks_router

app = FastAPI(
    title="Task Management API",
    description="A cloud-native API for managing personal tasks.",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
