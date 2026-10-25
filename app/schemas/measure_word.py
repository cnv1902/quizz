from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MeasureWordBase(BaseModel):
    vietnamese: str = Field(..., min_length=1, description="Giải thích nghĩa và ví dụ tiếng Việt")
    pinyin: str = Field(..., min_length=1, description="Phiên âm Pinyin")
    hanzi: str = Field(..., min_length=1, description="Chữ Hán lượng từ")
    order_index: Optional[int] = Field(0, description="Thứ tự hiển thị")
    audio_url: Optional[str] = None


class MeasureWordCreate(MeasureWordBase):
    pass


class MeasureWordUpdate(BaseModel):
    vietnamese: Optional[str] = None
    pinyin: Optional[str] = None
    hanzi: Optional[str] = None
    order_index: Optional[int] = None
    audio_url: Optional[str] = None


class MeasureWordResponse(MeasureWordBase):
    id: int
    audio_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MeasureWordBulkCreateRequest(BaseModel):
    items: List[MeasureWordCreate]


class MeasureWordBulkDeleteRequest(BaseModel):
    ids: List[int]
