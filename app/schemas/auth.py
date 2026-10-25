from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    """Schema đăng nhập bằng username/password."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema trả về JWT token sau khi đăng nhập thành công."""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    full_name: str
    is_admin: bool


class GoogleCallbackResponse(BaseModel):
    """Schema trả về sau Google OAuth2 callback."""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    full_name: str
    is_admin: bool
    is_new_user: bool = False
