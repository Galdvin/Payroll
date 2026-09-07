from typing import List
from sqlalchemy.orm import Session
from app.core.exceptions import PayrollException, ResourceNotFoundException
from app.models.rbac import Role, Permission
from app.schemas.rbac import RoleCreate


class RBACService:

    @staticmethod
    def get_all_roles(db: Session) -> List[Role]:
        return db.query(Role).all()

    @staticmethod
    def get_all_permissions(db: Session) -> List[Permission]:
        return db.query(Permission).all()

    @staticmethod
    def create_role(db: Session, data: RoleCreate) -> Role:
        existing = db.query(Role).filter(Role.name == data.name).first()
        if existing:
            raise PayrollException(f"Role '{data.name}' already exists.", error_code="ROLE_EXISTS")

        role = Role(
            name=data.name,
            description=data.description,
            is_system_role=False,
        )

        if data.permission_ids:
            perms = db.query(Permission).filter(Permission.id.in_(data.permission_ids)).all()
            role.permissions.extend(perms)

        db.add(role)
        db.commit()
        db.refresh(role)
        return role
