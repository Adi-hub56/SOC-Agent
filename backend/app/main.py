
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

# Import database setup
from app.database import init_db
from app.utils.logger import log_info

# Create app with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    log_info("Starting SOC Agent...")
    init_db()
    
    # Verify LLM API key
    llm_provider = os.getenv("LLM_PROVIDER", "groq").lower()
    if llm_provider == "groq":
        if not os.getenv("GROQ_API_KEY"):
            log_info("⚠️  WARNING: GROQ_API_KEY not set. Add to .env file")
        else:
            log_info("✅ Groq API key loaded")
    
    yield
    # Shutdown
    log_info("Shutting down SOC Agent...")

app = FastAPI(
    title="AI-Powered SOC Agent API",
    description="Production-grade security incident analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "SOC Agent API",
        "version": "1.0.0",
        "llm_provider": os.getenv("LLM_PROVIDER", "groq")
    }

# Test endpoint
@app.get("/api/test")
def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "message": "✅ API is working!",
        "llm": os.getenv("LLM_PROVIDER", "groq")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

