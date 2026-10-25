from sqlalchemy.orm import Session
from typing import List, Optional
from app.crud import crud_quiz, crud_card
from app.models.quiz import Quiz
from app.schemas.quiz import QuizListResponse


def get_all_quizzes_with_count(db: Session) -> List[dict]:
    """
    Lấy danh sách tất cả quiz đang active kèm số lượng thẻ.
    """
    quizzes = crud_quiz.get_all_active(db)
    result = []
    for quiz in quizzes:
        card_count = crud_quiz.count_cards(db, quiz.id)
        result.append({
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "card_count": card_count,
            "is_active": quiz.is_active,
            "created_at": quiz.created_at,
        })
    return result


def get_all_quizzes_admin(db: Session) -> List[dict]:
    """Lấy toàn bộ quiz (kể cả inactive) cho admin."""
    quizzes = crud_quiz.get_all(db)
    result = []
    for quiz in quizzes:
        card_count = crud_quiz.count_cards(db, quiz.id)
        result.append({
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "card_count": card_count,
            "is_active": quiz.is_active,
            "created_at": quiz.created_at,
            "updated_at": quiz.updated_at,
            "created_by": quiz.created_by,
        })
    return result


def create_quiz(
    db: Session, title: str, description: Optional[str], created_by: int
) -> Quiz:
    """Tạo quiz mới."""
    return crud_quiz.create(db, title=title, description=description, created_by=created_by)


def update_quiz(db: Session, quiz_id: int, **fields) -> Optional[Quiz]:
    """Cập nhật quiz. Trả về None nếu không tìm thấy."""
    quiz = crud_quiz.get_by_id(db, quiz_id)
    if not quiz:
        return None
    return crud_quiz.update(db, quiz, **fields)


def delete_quiz(db: Session, quiz_id: int) -> bool:
    """Xóa quiz. Trả về False nếu không tìm thấy."""
    quiz = crud_quiz.get_by_id(db, quiz_id)
    if not quiz:
        return False
    return crud_quiz.delete(db, quiz)


def get_quiz_detail(db: Session, quiz_id: int) -> Optional[dict]:
    """Lấy chi tiết quiz kèm card_count."""
    quiz = crud_quiz.get_by_id(db, quiz_id)
    if not quiz:
        return None
    card_count = crud_quiz.count_cards(db, quiz_id)
    return {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "card_count": card_count,
        "is_active": quiz.is_active,
        "created_by": quiz.created_by,
        "created_at": quiz.created_at,
        "updated_at": quiz.updated_at,
    }
