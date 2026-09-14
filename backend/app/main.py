"""
AIVOA — AI-Powered Customer Complaint Management System
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import complaints, copilot

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Customer Complaint Management System for Pharmaceutical Manufacturing (API & FDF)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(complaints.router)
app.include_router(copilot.router)


@app.on_event("startup")
def on_startup():
    """Initialize database tables on startup."""
    init_db()
    print(f"[OK] {settings.APP_NAME} started successfully")
    print(f"[DOCS] API docs: http://localhost:8000/docs")
    print(f"[AI] Groq model: {settings.GROQ_MODEL}")


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "name": settings.APP_NAME,
        "status": "running",
        "version": "1.0.0",
        "ai_model": settings.GROQ_MODEL,
    }


@app.get("/health")
def health():
    """Health check."""
    return {"status": "healthy"}
