import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager

backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.exceptions import PayrollException, payroll_exception_handler
from app.core.middleware import SecurityAndAuditMiddleware
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.services.auth_service import AuthService
from app.api.router import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payroll")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events."""
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    logger.info("Bootstrapping system roles, permissions, and SuperAdmin...")
    db = SessionLocal()
    try:
        AuthService.seed_superadmin(db)
    except Exception as e:
        logger.error(f"Error during initial bootstrap: {e}")
    finally:
        db.close()

    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security and audit middleware
app.add_middleware(SecurityAndAuditMiddleware)

# Custom exception handlers
app.add_exception_handler(PayrollException, payroll_exception_handler)

# Include API endpoints
app.include_router(api_router)


# Serve Web Application Interface at root URL
static_dir = Path(__file__).resolve().parent / "static"

@app.get("/", response_class=HTMLResponse, tags=["Web Portal UI"])
def get_web_portal():
    """Serves the interactive Web Application Interface."""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Enterprise Payroll Management System</h1><p>Visit <a href='/docs'>/docs</a> for API documentation.</p>")


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health Check"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }

