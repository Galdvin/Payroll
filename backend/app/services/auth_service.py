from datetime import timedelta
from typing import List, Tuple, Set, Optional, Dict, Any

from sqlalchemy.orm import Session
from app.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.exceptions import InvalidCredentialsException, TokenExpiredException
from app.models.user import User, RefreshToken
from app.models.rbac import Role, Permission
from app.schemas.auth import LoginRequest, TokenResponse, CurrentUserPermissions

SYSTEM_PERMISSIONS = [
    # Employee Management
    ("employee.view", "employee", "View employee profiles"),
    ("employee.create", "employee", "Create new employee record"),
    ("employee.update", "employee", "Update employee profile"),
    ("employee.delete", "employee", "Terminate or delete employee"),
    # Organization Management
    ("organization.view", "organization", "View organizational structure"),
    ("organization.create", "organization", "Create departments, branches, cost centers"),
    ("organization.update", "organization", "Update organizational structure"),
    ("organization.delete", "organization", "Delete organizational units"),
    # Attendance & Leave
    ("attendance.view", "attendance", "View attendance records"),
    ("attendance.create", "attendance", "Log attendance and create shifts"),
    ("attendance.update", "attendance", "Update attendance and shifts"),
    ("attendance.delete", "attendance", "Delete attendance and shifts"),
    ("leave.view", "leave", "View leave requests and policies"),
    ("leave.apply", "leave", "Apply for leaves"),
    ("leave.approve", "leave", "Approve employee leave applications"),
    ("leave.update", "leave", "Update leave policies and types"),
    ("leave.delete", "leave", "Delete leave applications and policies"),
    # Salary & Financial Extras
    ("salary.view", "salary", "View employee salary structures"),
    ("salary.create", "salary", "Create salary components and structures"),
    ("salary.update", "salary", "Update salary structures and components"),
    ("salary.delete", "salary", "Delete salary components and structures"),
    ("financial.view", "financial", "View loans, advances, bonuses, reimbursements"),
    ("financial.create", "financial", "Create loans, bonuses, reimbursements"),
    ("financial.update", "financial", "Update loans, bonuses, reimbursements"),
    ("financial.delete", "financial", "Delete financial extra records"),
    # Payroll Management
    ("payroll.view", "payroll", "View payroll runs and periods"),
    ("payroll.create", "payroll", "Initiate payroll run"),
    ("payroll.calculate", "payroll", "Execute payroll calculation engine"),
    ("payroll.approve", "payroll", "Approve payroll processing step"),
    ("payroll.lock", "payroll", "Lock payroll run after finalization"),
    ("payroll.process_payment", "payroll", "Generate bank payment files and mark paid"),
    ("payroll.delete", "payroll", "Delete payroll runs and periods"),
    # Tax & Statutory Rules
    ("statutory.view", "tax_statutory", "View tax and statutory rules"),
    ("statutory.create", "tax_statutory", "Create tax and statutory rules"),
    ("statutory.update", "tax_statutory", "Update tax and statutory rules"),
    ("statutory.delete", "tax_statutory", "Delete tax and statutory rules"),
    # User & Role Management
    ("user.view", "users", "View user accounts"),
    ("user.create", "users", "Create user accounts"),
    ("user.update", "users", "Update user accounts"),
    ("user.delete", "users", "Delete user accounts"),
    ("roles.view", "roles", "View roles and permissions"),
    ("roles.create", "roles", "Create roles and permissions"),
    ("roles.update", "roles", "Update roles and permissions"),
    ("roles.delete", "roles", "Delete roles"),
    # Reports & Audit
    ("reports.view", "reports", "View payroll and statutory reports"),
    ("audit.view", "audit", "Inspect security and calculation audit logs"),
]


SYSTEM_ROLES = [
    ("Super Admin", "Full system access across all organizations"),
    ("Organization Admin", "Administrator for specific organization"),
    ("HR Admin", "Full HR and employee management access"),
    ("Payroll Admin", "Full payroll execution and management access"),
    ("HR Manager", "Departmental HR management"),
    ("Payroll Manager", "Payroll approval and review"),
    ("Finance Manager", "Financial and accounting review"),
    ("Department Manager", "Team management and leave approvals"),
    ("Employee", "Self service access"),
    ("Auditor", "Read-only access to audit logs and financial reports"),
]


class AuthService:

    @staticmethod
    def seed_initial_roles_and_permissions(db: Session) -> Tuple[int, int]:
        """Seed system permissions and roles if not present."""
        created_permissions = 0
        created_roles = 0

        # 1. Seed Permissions
        perm_map = {}
        for code, module, desc in SYSTEM_PERMISSIONS:
            existing = db.query(Permission).filter(Permission.code == code).first()
            if not existing:
                perm = Permission(code=code, module=module, description=desc)
                db.add(perm)
                db.flush()
                perm_map[code] = perm
                created_permissions += 1
            else:
                perm_map[code] = existing

        # 2. Seed Roles
        for role_name, desc in SYSTEM_ROLES:
            existing_role = db.query(Role).filter(Role.name == role_name).first()
            if not existing_role:
                role = Role(name=role_name, description=desc, is_system_role=True)
                if role_name == "Super Admin":
                    role.permissions = list(perm_map.values())
                db.add(role)
                created_roles += 1

        db.commit()
        return created_permissions, created_roles

    @staticmethod
    def seed_superadmin(db: Session) -> User:
        """Seed or return default superadmin user."""
        AuthService.seed_initial_roles_and_permissions(db)
        admin = db.query(User).filter(User.email == settings.INITIAL_ADMIN_EMAIL).first()
        if not admin:
            admin_role = db.query(Role).filter(Role.name == "Super Admin").first()
            admin = User(
                email=settings.INITIAL_ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.INITIAL_ADMIN_PASSWORD),
                full_name="System Super Admin",
                is_active=True,
                is_superuser=True,
            )
            if admin_role:
                admin.roles.append(admin_role)
            db.add(admin)
            db.commit()
            db.refresh(admin)
        return admin

    @staticmethod
    def authenticate_user(db: Session, creds: LoginRequest) -> TokenResponse:
        """Authenticate user email & password and return token pair."""
        user = db.query(User).filter(User.email == creds.email).first()
        if not user or not verify_password(creds.password, user.hashed_password):
            raise InvalidCredentialsException()

        if not user.is_active:
            raise InvalidCredentialsException("User account is deactivated.")

        access_token = create_access_token(subject=user.id)
        refresh_token_str = create_refresh_token(subject=user.id)

        # Store refresh token record
        ref_record = RefreshToken(
            token=refresh_token_str,
            user_id=user.id,
        )
        db.add(ref_record)
        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    @staticmethod
    def refresh_access_token(db: Session, refresh_token_str: str) -> TokenResponse:
        """Issue new access token using non-revoked refresh token."""
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise TokenExpiredException("Invalid or expired refresh token.")

        user_id = int(payload.get("sub"))
        token_record = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token_str,
            RefreshToken.is_revoked == False
        ).first()

        if not token_record:
            raise TokenExpiredException("Refresh token has been revoked or is invalid.")

        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise InvalidCredentialsException("User associated with token is inactive.")

        new_access_token = create_access_token(subject=user.id)
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token_str,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    @staticmethod
    def get_user_permissions(user: User) -> CurrentUserPermissions:
        """Collect all role names and permission codes assigned to user."""
        role_names = [role.name for role in user.roles]
        permissions_set: Set[str] = set()

        if user.is_superuser:
            permissions_set.add("*")
        
        for role in user.roles:
            for perm in role.permissions:
                permissions_set.add(perm.code)

        return CurrentUserPermissions(
            id=user.id,
            uuid=user.uuid,
            email=user.email,
            full_name=user.full_name,
            is_superuser=user.is_superuser,
            roles=role_names,
            permissions=list(permissions_set),
        )

    @staticmethod
    def logout(db: Session, refresh_token_str: Optional[str] = None) -> Dict[str, Any]:
        """Revoke refresh token and invalidate user session."""
        if refresh_token_str:
            token_record = db.query(RefreshToken).filter(RefreshToken.token == refresh_token_str).first()
            if token_record:
                token_record.is_revoked = True
                db.commit()
        return {"success": True, "message": "User session invalidated successfully."}

    @staticmethod
    def reset_password(db: Session, email: str, new_password: str) -> Dict[str, Any]:
        """Reset user password."""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise InvalidCredentialsException("User with specified email not found.")
        
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        return {"success": True, "message": "Password reset successfully."}

