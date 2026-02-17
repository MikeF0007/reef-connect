from fastapi import FastAPI

try:
    from backend.api_service.app.core.config import settings
    app = FastAPI(title=settings.app_name, debug=settings.debug)
except ImportError:
    app = FastAPI(title="ReefConnect API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Welcome to ReefConnect API"}
