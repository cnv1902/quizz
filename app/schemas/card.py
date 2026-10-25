from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CardBase(BaseModel):
    """Các trường cơ bản dùng chung cho Card."""
    vietnamese: str
    pinyin: str
    hanzi: str
    order_index: int = 0
    audio_url: Optional[str] = None


class CardCreate(CardBase):
    """Schema để tạo thẻ mới."""
    quiz_id: int


class CardUpdate(BaseModel):
    """Schema để cập nhật thẻ."""
    vietnamese: Optional[str] = None
    pinyin: Optional[str] = None
    hanzi: Optional[str] = None
    order_index: Optional[int] = None
    audio_url: Optional[str] = None


class CardResponse(CardBase):
    """Schema trả về thông tin đầy đủ của thẻ."""
    id: int
    quiz_id: int
    audio_url: Optional[str] = None
    created_at: datetime
    # Thống kê cá nhân (optional, chỉ có khi user đã đăng nhập)
    correct_count: Optional[int] = 0
    wrong_count: Optional[int] = 0
    priority: Optional[int] = 0

    model_config = {"from_attributes": True}


class CardBulkCreate(BaseModel):
    """Schema để import nhiều thẻ cùng lúc."""
    cards: list[CardBase]


class CardBulkCreateRequest(BaseModel):
    """Schema để import hàng loạt thẻ vào một quiz cụ thể."""
    quiz_id: int
    cards: list[CardBase]


class CardBulkDeleteRequest(BaseModel):
    """Schema để xóa hàng loạt thẻ theo danh sách IDs."""
    card_ids: list[int]


