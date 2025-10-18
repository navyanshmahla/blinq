from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str]
    subscription_tier: str
    queries_used_this_month: int
    last_query_reset_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    subscription_tier: Optional[str] = None

class ConversationCreate(BaseModel):
    title: str

class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    csv_id: Optional[UUID]
    csv_expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

class CSVFileCreate(BaseModel):
    conversation_id: UUID
    filename: str
    file_size: int
    row_count: int
    column_names: List[str]
    csv_data: bytes
    expires_at: datetime

class CSVFileResponse(BaseModel):
    id: UUID
    user_id: UUID
    conversation_id: UUID
    filename: str
    file_size: int
    row_count: int
    column_names: List[str]
    uploaded_at: datetime
    expires_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    conversation_id: UUID
    role: str
    content: str
    cost: Optional[float] = None
    request_id: Optional[UUID] = None
    is_plotting: Optional[bool] = None

class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    cost: Optional[float]
    request_id: Optional[UUID]
    is_plotting: Optional[bool]
    created_at: datetime

    class Config:
        from_attributes = True

class PlotCreate(BaseModel):
    message_id: Optional[UUID] = None
    request_id: UUID
    image_data: bytes

class PlotResponse(BaseModel):
    id: UUID
    message_id: UUID
    request_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class UsageTrackingCreate(BaseModel):
    user_id: UUID
    message_id: UUID
    cost: float
    model_used: str

class UsageTrackingResponse(BaseModel):
    id: UUID
    user_id: UUID
    message_id: UUID
    cost: float
    model_used: str
    created_at: datetime

    class Config:
        from_attributes = True

class RefreshTokenCreate(BaseModel):
    user_id: UUID
    token: str
    expires_at: datetime

class RefreshTokenResponse(BaseModel):
    id: UUID
    user_id: UUID
    token: str
    expires_at: datetime
    is_revoked: bool
    created_at: datetime

    class Config:
        from_attributes = True
