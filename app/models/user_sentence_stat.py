from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class UserSentenceStat(Base):
    """
    Model bảng user_sentence_stats — theo dõi tiến độ đúng/sai của user cho từng câu ghép.
    priority = wrong_count - correct_count (càng cao càng cần luyện tập).
    """
    __tablename__ = "user_sentence_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sentence_id = Column(Integer, ForeignKey("sentences.id"), nullable=False, index=True)
    correct_count = Column(Integer, default=0, nullable=False)
    wrong_count = Column(Integer, default=0, nullable=False)
    priority = Column(Integer, default=0, nullable=False)
    last_played = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "sentence_id", name="uq_user_sentence"),
    )

    user = relationship("User", backref="sentence_stats")
    sentence = relationship("Sentence", backref="user_stats")
