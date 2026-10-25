from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.models.base import Base


class MeasureWord(Base):
    """Model bảng measure_words — lượng từ tiếng Trung."""
    __tablename__ = "measure_words"

    id = Column(Integer, primary_key=True, index=True)
    vietnamese = Column(Text, nullable=False)   # Giải thích nghĩa & ví dụ tiếng Việt
    pinyin = Column(String(500), nullable=False)       # Phiên âm Pinyin
    hanzi = Column(String(200), nullable=False)        # Chữ Hán lượng từ
    audio_url = Column(String(500), nullable=True)     # URL file MP3 phát âm chuẩn
    order_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
