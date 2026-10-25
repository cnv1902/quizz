from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Các trường cơ bản dùng chung cho User."""
    username: str
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """Schema để tạo tài khoản mới (tự đăng ký)."""
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Mật khẩu phải có ít nhất 6 ký tự")
        return v

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Username phải có ít nhất 3 ký tự")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username chỉ được chứa chữ, số, _ và -")
        return v.lower()


class UserUpdate(BaseModel):
    """Schema để admin cập nhật user."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    cards_per_round: Optional[int] = None


class UserSettingsUpdate(BaseModel):
    """Schema để user tự cập nhật cấu hình."""
    cards_per_round: Optional[int] = None
    full_name: Optional[str] = None


class UserResponse(UserBase):
    """Schema trả về thông tin user (không có password)."""
    id: int
    is_admin: bool
    is_active: bool
    cards_per_round: int
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Schema danh sách users cho admin."""
    id: int
    username: str
    email: str
    full_name: str
    is_admin: bool
    is_active: bool
    cards_per_round: int
    created_at: datetime
    google_id: Optional[str] = None

    model_config = {"from_attributes": True}
