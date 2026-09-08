from typing import List
from sqlalchemy.orm import Session
from app.core.exceptions import PayrollException, ResourceNotFoundException
from app.models.rbac import Role, Permission
from app.schemas.rbac import RoleCreate, RoleUpdate


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

    @staticmethod
    def update_role(db: Session, role_id: int, data: RoleUpdate) -> Role:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ResourceNotFoundException(f"Role with ID {role_id} not found.")
        if data.name is not None:
            role.name = data.name
        if data.description is not None:
            role.description = data.description
        if data.permission_ids is not None:
            perms = db.query(Permission).filter(Permission.id.in_(data.permission_ids)).all()
            role.permissions = perms
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def delete_role(db: Session, role_id: int) -> dict:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ResourceNotFoundException(f"Role with ID {role_id} not found.")
        if role.is_system_role:
            raise PayrollException("Cannot delete a system role.", error_code="CANNOT_DELETE_SYSTEM_ROLE")
        db.delete(role)
        db.commit()
        return {"detail": f"Role '{role.name}' deleted successfully."}

