from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime
from app.models.user_card_stat import UserCardStat


def get_stat(db: Session, user_id: int, card_id: int) -> Optional[UserCardStat]:
    """Lấy stat của 1 thẻ theo user."""
    return (
        db.query(UserCardStat)
        .filter(UserCardStat.user_id == user_id, UserCardStat.card_id == card_id)
        .first()
    )


def get_or_create(db: Session, user_id: int, card_id: int) -> UserCardStat:
    """
    Lấy stat nếu đã có, tạo mới nếu chưa có.
    KHÔNG commit tại đây — để service quản lý transaction.
    """
    stat = get_stat(db, user_id, card_id)
    if not stat:
        stat = UserCardStat(
            user_id=user_id,
            card_id=card_id,
            correct_count=0,
            wrong_count=0,
            priority=0,
        )
        db.add(stat)
    return stat


def batch_update(
    db: Session,
    user_id: int,
    results: List[dict],
) -> bool:
    """
    Cập nhật hàng loạt kết quả đúng/sai sau mỗi game.
    results: [{"card_id": int, "is_correct": bool}, ...]
    """
    try:
        for item in results:
            stat = get_or_create(db, user_id, item["card_id"])
            if item["is_correct"]:
                stat.correct_count += 1
            else:
                stat.wrong_count += 1
            stat.priority = stat.wrong_count - stat.correct_count
            stat.last_played = datetime.utcnow()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e


def get_quiz_stats(db: Session, user_id: int, quiz_id: int) -> dict:
    """Lấy thống kê tổng quan của user trong 1 quiz."""
    from app.models.card import Card
    total_cards = db.query(func.count(Card.id)).filter(Card.quiz_id == quiz_id).scalar() or 0
    studied = (
        db.query(func.count(UserCardStat.id))
        .join(Card, UserCardStat.card_id == Card.id)
        .filter(UserCardStat.user_id == user_id, Card.quiz_id == quiz_id)
        .scalar() or 0
    )
    total_correct = (
        db.query(func.sum(UserCardStat.correct_count))
        .join(Card, UserCardStat.card_id == Card.id)
        .filter(UserCardStat.user_id == user_id, Card.quiz_id == quiz_id)
        .scalar() or 0
    )
    total_wrong = (
        db.query(func.sum(UserCardStat.wrong_count))
        .join(Card, UserCardStat.card_id == Card.id)
        .filter(UserCardStat.user_id == user_id, Card.quiz_id == quiz_id)
        .scalar() or 0
    )
    avg_priority = (
        db.query(func.avg(UserCardStat.priority))
        .join(Card, UserCardStat.card_id == Card.id)
        .filter(UserCardStat.user_id == user_id, Card.quiz_id == quiz_id)
        .scalar() or 0.0
    )
    return {
        "quiz_id": quiz_id,
        "total_cards": total_cards,
        "cards_studied": studied,
        "total_correct": int(total_correct),
        "total_wrong": int(total_wrong),
        "average_priority": float(avg_priority),
    }
