from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeHistoryResponse,
)
from app.schemas.document import DocumentResponse
from app.services.employee_service import EmployeeService
from app.security.permissions import RequirePermission, get_current_user
from app.models.user import User

router = APIRouter(prefix="/employees", tags=["Employee Master"])


@router.get("", status_code=status.HTTP_200_OK)
def list_employees(
    organization_id: Optional[int] = None,
    department_id: Optional[int] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    employment_type: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("employee.view")),
):
    employees, total = EmployeeService.get_employees(
        db,
        organization_id=organization_id,
        department_id=department_id,
        status=status_filter,
        employment_type=employment_type,
        search=search,
        skip=skip,
        limit=limit,
    )
    return {
        "items": [EmployeeResponse.model_validate(emp) for emp in employees],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    body: EmployeeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("employee.create")),
):
    return EmployeeService.create_employee(db, body)


@router.get("/{employee_id}", response_model=EmployeeResponse, status_code=status.HTTP_200_OK)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("employee.view")),
):
    return EmployeeService.get_by_id(db, employee_id)


@router.put("/{employee_id}", response_model=EmployeeResponse, status_code=status.HTTP_200_OK)
def update_employee(
    employee_id: int,
    body: EmployeeUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("employee.update")),
):
    return EmployeeService.update_employee(db, employee_id, body)


@router.get("/{employee_id}/history", response_model=List[EmployeeHistoryResponse], status_code=status.HTTP_200_OK)
def get_employee_history(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("employee.view")),
):
    return EmployeeService.get_employee_history(db, employee_id)


@router.get("/{employee_id}/documents", response_model=List[DocumentResponse], status_code=status.HTTP_200_OK)
def list_employee_documents(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("employee.view")),
):
    return EmployeeService.get_employee_documents(db, employee_id)


@router.post("/{employee_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_employee_document(
    employee_id: int,
    document_type: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee.update")),
):
    # Standard file upload simulation for metadata
    file_path = f"/uploads/employees/{employee_id}/{file.filename}"
    file_size = file.size if file.size else 1024
    return EmployeeService.add_employee_document(
        db,
        employee_id=employee_id,
        document_type=document_type,
        title=title,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type or "application/pdf",
        uploaded_by_user_id=current_user.id,
    )
