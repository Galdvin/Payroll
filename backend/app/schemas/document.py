from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class DocumentCreate(BaseModel):
    document_type: str
    title: str
    expiration_date: Optional[date] = None


class DocumentResponse(BaseModel):
    id: int
    employee_id: int
    document_type: str
    title: str
    file_path: str
    file_size: int
    mime_type: str
    version: int
    expiration_date: Optional[date] = None
    created_at: datetime

    model_config = {"from_attributes": True}
