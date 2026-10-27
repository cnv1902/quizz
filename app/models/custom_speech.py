from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.types import JSON
from datetime import datetime
from app.models.base import Base


class CustomSpeechArticle(Base):
    """
    Bảng custom_speech_articles — Lưu bài viết song ngữ/đoạn văn dài tự do của người dùng.
    Hỗ trợ phát âm thanh 1 file MP3 duy nhất và đồng bộ Karaoke highlight theo thời gian thực.
    Chỉ dành riêng cho người dùng đã đăng nhập (cách ly theo user_id).
    """
    __tablename__ = "custom_speech_articles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)               # Toàn bộ nội dung gốc người dùng nhập
    audio_url = Column(String(500), nullable=False)     # 1 file MP3 duy nhất ghép nối toàn bài
    duration_seconds = Column(Float, default=0.0, nullable=False)
    segments = Column(JSON, nullable=False)              # Mảng các đoạn [{ id, text, lang, start_time, end_time }]
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
