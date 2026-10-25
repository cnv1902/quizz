from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class GrammarPointBase(BaseModel):
    vietnamese: str = Field(..., min_length=1, description="Giải thích cấu trúc, công thức & ví dụ tiếng Việt")
    pinyin: str = Field(..., min_length=1, description="Phiên âm Pinyin")
    hanzi: str = Field(..., min_length=1, description="Từ khóa hoặc cấu trúc chữ Hán")
    order_index: Optional[int] = Field(0, description="Thứ tự hiển thị")
    audio_url: Optional[str] = None


class GrammarPointCreate(GrammarPointBase):
    pass


class GrammarPointUpdate(BaseModel):
    vietnamese: Optional[str] = None
    pinyin: Optional[str] = None
    hanzi: Optional[str] = None
    order_index: Optional[int] = None
    audio_url: Optional[str] = None


class GrammarPointResponse(GrammarPointBase):
    id: int
    audio_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GrammarPointBulkCreateRequest(BaseModel):
    items: List[GrammarPointCreate]


class GrammarPointBulkDeleteRequest(BaseModel):
    ids: List[int]
