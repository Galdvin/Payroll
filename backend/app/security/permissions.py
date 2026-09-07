from typing import Callable, Set
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import (
    InsufficientPermissionsException,
    InvalidCredentialsException,
    TokenExpiredException,
)
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Dependency extracting user from bearer JWT access token."""
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise TokenExpiredException("Invalid or expired access token.")

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidCredentialsException("Invalid token payload.")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise InvalidCredentialsException("User not found.")

    if not user.is_active:
        raise InvalidCredentialsException("User account is inactive.")

    return user


class RequirePermission:
    """FastAPI dependency asserting that the authenticated user possesses a specific granular permission code."""

    def __init__(self, permission_code: str):
        self.permission_code = permission_code

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user

        user_permissions: Set[str] = set()
        for role in current_user.roles:
            for perm in role.permissions:
                user_permissions.add(perm.code)

        if self.permission_code not in user_permissions:
            raise InsufficientPermissionsException(
                f"Required permission '{self.permission_code}' is missing."
            )

        return current_user
