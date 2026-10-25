from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SentenceSetBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Tên bộ câu")
    description: Optional[str] = Field(None, description="Mô tả bộ câu")
    is_active: bool = Field(True, description="Trạng thái kích hoạt")
    order_index: int = Field(0, description="Thứ tự hiển thị")


class SentenceSetCreate(SentenceSetBase):
    pass


class SentenceSetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    order_index: Optional[int] = None


class SentenceSetResponse(SentenceSetBase):
    id: int
    created_at: datetime
    sentence_count: int = 0
    samples: str = "你 · 好 · 吗 · ？"

    class Config:
        from_attributes = True
