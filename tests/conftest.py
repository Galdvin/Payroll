import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Override database URL to SQLite file/memory for automated tests
os.environ["DATABASE_URL"] = "sqlite:///./test_payroll.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-payroll-unit-and-api-tests"

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.auth_service import AuthService
from app.models.user import User
from app.models.rbac import Role, Permission
from app.core.security import get_password_hash

TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test_payroll.db"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database schema and cleanup after test run."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    AuthService.seed_superadmin(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_payroll.db"):
        try:
            os.remove("./test_payroll.db")
        except PermissionError:
            pass


@pytest.fixture
def db():
    """Provide a fresh transaction-isolated session per test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """FastAPI TestClient with overridden get_db dependency."""
    def _get_test_db():
        yield db

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers(client):
    """Generate authorization headers for default SuperAdmin."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@enterprise-payroll.com", "password": "AdminPassword123!"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def employee_user(db):
    """Fixture providing a standard employee user with limited 'leave.apply' permission."""
    emp_role = db.query(Role).filter(Role.name == "Employee").first()
    if not emp_role:
        emp_role = Role(name="Employee", description="Standard employee role")
        db.add(emp_role)
        db.flush()

    leave_perm = db.query(Permission).filter(Permission.code == "leave.apply").first()
    if leave_perm and leave_perm not in emp_role.permissions:
        emp_role.permissions.append(leave_perm)

    user = User(
        email="john.doe@company.com",
        hashed_password=get_password_hash("EmployeePass123!"),
        full_name="John Doe",
        is_active=True,
        is_superuser=False,
    )
    user.roles.append(emp_role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def employee_headers(client, employee_user):
    """Generate authorization headers for standard employee user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": employee_user.email, "password": "EmployeePass123!"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
