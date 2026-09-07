import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
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


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health Check"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }
