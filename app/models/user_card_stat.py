from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class UserCardStat(Base):
    """
    Model bảng user_card_stats — theo dõi lịch sử đúng/sai của mỗi user cho mỗi thẻ.
    priority = wrong_count - correct_count (càng cao càng cần ôn tập).
    """
    __tablename__ = "user_card_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False, index=True)
    correct_count = Column(Integer, default=0, nullable=False)
    wrong_count = Column(Integer, default=0, nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # wrong - correct (cached)
    last_played = Column(DateTime, nullable=True)

    # Unique constraint: mỗi user chỉ có 1 stat cho 1 thẻ
    __table_args__ = (
        UniqueConstraint("user_id", "card_id", name="uq_user_card"),
    )

    # Relationships
    user = relationship("User", back_populates="card_stats")
    card = relationship("Card", back_populates="user_stats")
