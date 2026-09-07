from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.rbac import RoleCreate, RoleResponse, PermissionResponse
from app.services.rbac_service import RBACService
from app.security.permissions import RequirePermission, get_current_user
from app.models.user import User

router = APIRouter(prefix="/roles", tags=["Roles & Permissions"])


@router.get("", response_model=List[RoleResponse], status_code=status.HTTP_200_OK)
def list_roles(
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("employee.view")),
):
    """List all configured roles."""
    return RBACService.get_all_roles(db)


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    body: RoleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("employee.create")),
):
    """Create a new custom role with associated permissions."""
    return RBACService.create_role(db, body)


@router.get("/permissions", response_model=List[PermissionResponse], status_code=status.HTTP_200_OK)
def list_permissions(
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("employee.view")),
):
    """List all available granular system permissions."""
    return RBACService.get_all_permissions(db)
