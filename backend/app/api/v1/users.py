from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService
from app.security.permissions import RequirePermission, get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("employee.view")),
):
    """Retrieve list of user accounts (Requires 'employee.view' permission)."""
    return UserService.get_users(db, skip=skip, limit=limit)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("employee.create")),
):
    """Create a new user account (Requires 'employee.create' permission)."""
    return UserService.create_user(db, body)


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("employee.view")),
):
    """Retrieve user details by ID."""
    return UserService.get_by_id(db, user_id)


@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(
    user_id: int,
    body: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("employee.update")),
):
    """Update user profile and role assignments (Requires 'employee.update' permission)."""
    return UserService.update_user(db, user_id, body)
