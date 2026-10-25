from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.models.quiz import Quiz
from app.models.card import Card


def get_by_id(db: Session, quiz_id: int) -> Optional[Quiz]:
    """Lấy quiz theo ID."""
    return db.query(Quiz).filter(Quiz.id == quiz_id).first()


def get_all_active(db: Session, skip: int = 0, limit: int = 100) -> List[Quiz]:
    """Lấy danh sách tất cả quiz đang active (cho user)."""
    return (
        db.query(Quiz)
        .filter(Quiz.is_active == True)  # noqa: E712
        .order_by(Quiz.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Quiz]:
    """Lấy tất cả quiz kể cả inactive (cho admin)."""
    return db.query(Quiz).order_by(Quiz.created_at.desc()).offset(skip).limit(limit).all()


def count_cards(db: Session, quiz_id: int) -> int:
    """Đếm số thẻ trong quiz."""
    return db.query(func.count(Card.id)).filter(Card.quiz_id == quiz_id).scalar() or 0


def create(db: Session, title: str, description: Optional[str], created_by: int) -> Optional[Quiz]:
    """Tạo quiz mới."""
    try:
        db_quiz = Quiz(
            title=title,
            description=description,
            created_by=created_by,
            is_active=True,
        )
        db.add(db_quiz)
        db.commit()
        db.refresh(db_quiz)
        return db_quiz
    except Exception as e:
        db.rollback()
        raise e


def update(db: Session, quiz: Quiz, **fields) -> Optional[Quiz]:
    """Cập nhật quiz."""
    try:
        for key, value in fields.items():
            if value is not None and hasattr(quiz, key):
                setattr(quiz, key, value)
        db.commit()
        db.refresh(quiz)
        return quiz
    except Exception as e:
        db.rollback()
        raise e


def delete(db: Session, quiz: Quiz) -> bool:
    """Xóa quiz và tất cả thẻ liên quan (cascade)."""
    try:
        db.delete(quiz)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e


def count_all(db: Session) -> int:
    """Đếm tổng số quizzes."""
    return db.query(Quiz).count()
