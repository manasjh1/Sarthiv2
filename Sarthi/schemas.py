from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from db.model import UserTypeEnum, ReflectionModeEnum, DeliveryModeEnum

# ================================
# User Schemas (UPDATED)
# ================================

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[int] = None
    user_type: UserTypeEnum = UserTypeEnum.user
    proficiency_score: int = 0

class UserCreate(UserBase):
    pass  # ✅ REMOVED user_id - will be auto-generated in backend

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[int] = None
    proficiency_score: Optional[int] = None

class UserResponse(BaseModel):
    user_id: UUID  # ✅ Still returned in response for other endpoints to use
    name: str
    email: str
    phone_number: Optional[int] = None
    user_type: UserTypeEnum
    proficiency_score: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: int
    
    class Config:
        from_attributes = True

# For backward compatibility
User = UserResponse

# ================================
# Category Schemas
# ================================

class CategoryDict(BaseModel):
    category_no: int
    category_name: str
    status: int
    
    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    category_no: int
    category_name: str
    
    class Config:
        from_attributes = True

# ================================
# Stage Schemas
# ================================

class StageDict(BaseModel):
    stage_no: int
    stage_name: str
    status: int
    
    class Config:
        from_attributes = True

class StageResponse(BaseModel):
    stage_no: int
    stage_name: str
    
    class Config:
        from_attributes = True

# ================================
# Reflection Input Schemas
# ================================

class StartReflectionInput(BaseModel):
    user_id: UUID  # ✅ Keep this - we need to know which user

class CategoryInput(BaseModel):
    reflection_id: UUID  # ✅ Keep this - we need to know which reflection
    category_name: str

class NextStageInput(BaseModel):
    reflection_id: UUID  # ✅ Keep this - we need to know which reflection
    user_input: str

# ================================
# Reflection Response Schemas (UPDATED)
# ================================

class ReflectionStartResponse(BaseModel):
    reflection_id: UUID  # ✅ Changed to UUID for consistency
    stage_no: int
    stage_name: str
    prompt: str
    mode: str
    message: Optional[str] = None

class StageAdvanceResponse(BaseModel):
    stage_no: Optional[int] = None
    stage_name: Optional[str] = None
    prompt: Optional[str] = None
    message: Optional[str] = None

# For backward compatibility
StageResponse = StageAdvanceResponse

# ================================
# Full Reflection Schema
# ================================

class ReflectionBase(BaseModel):
    giver_user_id: UUID
    stage_no: int
    category_no: int
    receiver_user_id: Optional[UUID] = None
    mode: ReflectionModeEnum
    name: Optional[str] = None
    relation: Optional[str] = None
    reflection: Optional[str] = None
    delivery_mode: DeliveryModeEnum

class ReflectionResponse(ReflectionBase):
    reflection_id: UUID
    status: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# For backward compatibility
Reflection = ReflectionResponse

# ================================
# API Response Schemas
# ================================

class SuccessResponse(BaseModel):
    message: str
    status: str = "success"

class ErrorResponse(BaseModel):
    detail: str
    status: str = "error"

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime = datetime.now()