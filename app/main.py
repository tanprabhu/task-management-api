from fastapi import FastAPI

app = FastAPI(
    title="Task Management API",
    description="A cloud-native API for managing personal tasks.",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
