from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app.routes.incident import router as incident_router
from app.celery_app import app as celery_app  # ADD THIS LINE
from app.utils.logger import log_info
from app.routes.health import router as health_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    log_info("Starting SOC Agent API")
    init_db()
    log_info("Database initialized")
    yield
    log_info("Shutting down SOC Agent API")

app = FastAPI(
    title="SOC Agent API",
    description="AI-Powered Security Operations Center Analyst Agent",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "SOC Agent API",
        "version": "1.0.0",
        "llm_provider": "groq"
    }

@app.get("/")
async def root():
    return {
        "message": "SOC Agent API",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/analyze"
    }

app.include_router(incident_router)
app.include_router(health_router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
