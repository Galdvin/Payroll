from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.core.exceptions import PayrollException, ResourceNotFoundException
from app.models.user import User
from app.models.rbac import Role
from app.schemas.user import UserCreate, UserUpdate


class UserService:

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 50) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFoundException("User", user_id)
        return user

    @staticmethod
    def create_user(db: Session, data: UserCreate) -> User:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise PayrollException(f"User with email '{data.email}' already exists.", error_code="USER_EXISTS")

        user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            organization_id=data.organization_id,
            company_id=data.company_id,
        )

        if data.role_ids:
            roles = db.query(Role).filter(Role.id.in_(data.role_ids)).all()
            user.roles.extend(roles)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
        user = UserService.get_by_id(db, user_id)

        if data.full_name is not None:
            user.full_name = data.full_name
        if data.is_active is not None:
            user.is_active = data.is_active
        if data.organization_id is not None:
            user.organization_id = data.organization_id
        if data.company_id is not None:
            user.company_id = data.company_id

        if data.role_ids is not None:
            roles = db.query(Role).filter(Role.id.in_(data.role_ids)).all()
            user.roles = roles

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> dict:
        user = UserService.get_by_id(db, user_id)
        db.delete(user)
        db.commit()
        return {"success": True, "message": f"User {user_id} deleted successfully."}
