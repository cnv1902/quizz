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


def calculate_user_streak(db: Session, user_id: int) -> int:
    """
    Tính chuỗi ngày học liên tục (streak) của user dựa trên last_played trong user_card_stats & user_sentence_stats.
    """
    from datetime import date, datetime, timedelta
    from app.models.user_sentence_stat import UserSentenceStat

    card_dates = (
        db.query(func.date(UserCardStat.last_played))
        .filter(UserCardStat.user_id == user_id, UserCardStat.last_played.isnot(None))
        .distinct()
        .all()
    )
    sentence_dates = (
        db.query(func.date(UserSentenceStat.last_played))
        .filter(UserSentenceStat.user_id == user_id, UserSentenceStat.last_played.isnot(None))
        .distinct()
        .all()
    )

    raw_dates = set()
    for (d_val,) in card_dates + sentence_dates:
        if not d_val:
            continue
        if isinstance(d_val, str):
            try:
                parsed_d = datetime.strptime(d_val.split()[0], "%Y-%m-%d").date()
                raw_dates.add(parsed_d)
            except ValueError:
                pass
        elif isinstance(d_val, (date, datetime)):
            raw_dates.add(d_val.date() if isinstance(d_val, datetime) else d_val)

    if not raw_dates:
        return 0

    today = date.today()
    if today in raw_dates:
        curr = today
    elif (today - timedelta(days=1)) in raw_dates:
        curr = today - timedelta(days=1)
    else:
        return 0

    streak = 0
    while curr in raw_dates:
        streak += 1
        curr -= timedelta(days=1)

    return streak


def get_user_summary(db: Session, user_id: int) -> dict:
    """
    Lấy tổng quan tiến độ của user cho trang chủ:
    - total_cards: tổng số thẻ hệ thống
    - mastered_cards: số thẻ có priority <= -1 (đã thuộc)
    - review_needed: total_cards - mastered_cards (cần học/ôn hôm nay)
    - streak: chuỗi ngày học liên tục
    """
    from app.models.card import Card
    total_cards = db.query(func.count(Card.id)).scalar() or 0
    mastered_cards = (
        db.query(func.count(UserCardStat.id))
        .filter(UserCardStat.user_id == user_id, UserCardStat.priority <= -1)
        .scalar() or 0
    )
    review_needed = max(0, total_cards - mastered_cards)
    streak = calculate_user_streak(db, user_id)
    return {
        "streak": streak,
        "mastered_cards": mastered_cards,
        "review_needed": review_needed,
        "total_cards": total_cards,
    }

