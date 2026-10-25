from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QuizBase(BaseModel):
    """Các trường cơ bản dùng chung cho Quiz."""
    title: str
    description: Optional[str] = None


class QuizCreate(QuizBase):
    """Schema để tạo quiz mới."""
    pass


class QuizUpdate(BaseModel):
    """Schema để cập nhật quiz."""
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class QuizResponse(QuizBase):
    """Schema trả về thông tin quiz."""
    id: int
    created_by: int
    is_active: bool
    card_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class QuizListResponse(BaseModel):
    """Schema trả về danh sách quizzes với thống kê cơ bản."""
    id: int
    title: str
    description: Optional[str] = None
    card_count: int = 0
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
