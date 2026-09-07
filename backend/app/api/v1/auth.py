from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    CurrentUserPermissions,
)
from app.services.auth_service import AuthService
from app.security.permissions import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user with email and password, returning access and refresh JWT tokens."""
    return AuthService.authenticate_user(db, creds)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def refresh_token(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Issue a new access token using a valid refresh token."""
    return AuthService.refresh_access_token(db, body.refresh_token)


@router.get("/me", response_model=CurrentUserPermissions, status_code=status.HTTP_200_OK)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get profile details and permissions of current logged-in user."""
    return AuthService.get_user_permissions(current_user)


@router.post("/seed-admin", status_code=status.HTTP_201_CREATED)
def seed_admin(db: Session = Depends(get_db)):
    """Bootstrap initial system roles, permissions, and default SuperAdmin user."""
    admin = AuthService.seed_superadmin(db)
    return {
        "success": True,
        "message": f"SuperAdmin bootstrapped successfully with email '{admin.email}'."
    }
