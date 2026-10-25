from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class User(Base):
    """Model bảng users — lưu thông tin tài khoản người dùng."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String, nullable=True)   # NULL nếu đăng nhập Google
    google_id = Column(String(100), nullable=True, unique=True)  # NULL nếu tự đăng ký
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    cards_per_round = Column(Integer, default=10, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    quizzes = relationship("Quiz", back_populates="creator", foreign_keys="Quiz.created_by")
    card_stats = relationship("UserCardStat", back_populates="user")
