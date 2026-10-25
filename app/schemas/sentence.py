from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import json


class SentenceBase(BaseModel):
    set_id: Optional[int] = Field(None, description="ID của bộ câu chứa câu này")
    chinese: str = Field(..., min_length=1, description="Câu tiếng Trung chuẩn")
    vietnamese: str = Field(..., min_length=1, description="Dịch nghĩa tiếng Việt")
    pinyin: Optional[str] = Field(None, description="Phiên âm Pinyin")
    tokens: Optional[str] = Field(None, description="JSON array các khối từ đã phân tách")
    order_index: Optional[int] = Field(0, description="Thứ tự hiển thị")
    audio_url: Optional[str] = None


class SentenceCreate(SentenceBase):
    pass


class SentenceUpdate(BaseModel):
    set_id: Optional[int] = None
    chinese: Optional[str] = None
    vietnamese: Optional[str] = None
    pinyin: Optional[str] = None
    tokens: Optional[str] = None
    order_index: Optional[int] = None
    audio_url: Optional[str] = None


class SentenceResponse(SentenceBase):
    id: int
    audio_url: Optional[str] = None
    created_at: datetime
    token_list: Optional[List[str]] = None

    class Config:
        from_attributes = True


class SentencePuzzleItem(BaseModel):
    id: int
    set_id: Optional[int] = None
    chinese: str
    vietnamese: str
    pinyin: Optional[str] = None
    audio_url: Optional[str] = None
    shuffled_tokens: List[str] = []
    total_tokens: int = 0


class SentenceBulkCreateRequest(BaseModel):
    items: List[SentenceCreate]
    set_id: Optional[int] = None


class SentenceBulkDeleteRequest(BaseModel):
    ids: List[int]


class SentenceProgressItem(BaseModel):
    sentence_id: int
    is_correct: bool


class SentenceProgressBatch(BaseModel):
    results: List[SentenceProgressItem]
    set_id: Optional[int] = None
