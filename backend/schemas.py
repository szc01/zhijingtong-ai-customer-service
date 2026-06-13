from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = None


class ChatResponse(BaseModel):
    message: str
    response: str
    timestamp: datetime


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    content_summary: Optional[str]
    is_processed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ReportRequest(BaseModel):
    user_id: int
    report_type: str


class ReportResponse(BaseModel):
    id: int
    user_id: int
    report_type: str
    content: str
    generated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None