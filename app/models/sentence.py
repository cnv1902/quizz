from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Sentence(Base):
    """Model bảng sentences — câu tiếng Trung để luyện tập Ghép câu."""
    __tablename__ = "sentences"

    id = Column(Integer, primary_key=True, index=True)
    set_id = Column(Integer, ForeignKey("sentence_sets.id"), nullable=True, index=True)  # Khóa ngoại đến Bộ câu
    chinese = Column(String(500), nullable=False)       # Câu chữ Hán chuẩn (vd: 你在哪？)
    vietnamese = Column(String(500), nullable=False)    # Nghĩa tiếng Việt (vd: Bạn đang ở đâu?)
    pinyin = Column(String(500), nullable=True)         # Phiên âm Pinyin
    tokens = Column(Text, nullable=True)                # JSON string các khối từ sau tách (vd: ["你", "在", "哪"])
    audio_url = Column(String(500), nullable=True)      # URL file MP3 tiếng Trung (/static/voice/sentences/xxx.mp3)
    audio_vi_url = Column(String(500), nullable=True)   # URL file MP3 tiếng Việt (/static/voice/sentences_vi/xxx.mp3)
    order_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    sentence_set = relationship("SentenceSet", back_populates="sentences")
