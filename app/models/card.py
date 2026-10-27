from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Card(Base):
    """Model bảng cards — mỗi thẻ có 3 cột: Tiếng Việt, Pinyin, Chữ Hán."""
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False, index=True)
    vietnamese = Column(String(500), nullable=False)   # Nghĩa Tiếng Việt
    pinyin = Column(String(500), nullable=False)       # Phiên âm Pinyin (có dấu thanh)
    hanzi = Column(String(200), nullable=False)        # Chữ Hán
    audio_url = Column(String(500), nullable=True)     # URL file MP3 tiếng Trung
    audio_vi_url = Column(String(500), nullable=True)  # URL file MP3 tiếng Việt
    order_index = Column(Integer, default=0, nullable=False)  # Thứ tự trong quiz
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    quiz = relationship("Quiz", back_populates="cards")
    user_stats = relationship("UserCardStat", back_populates="card", cascade="all, delete-orphan")
