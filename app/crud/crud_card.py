from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from app.models.card import Card


def get_by_id(db: Session, card_id: int) -> Optional[Card]:
    """Lấy thẻ theo ID."""
    return db.query(Card).filter(Card.id == card_id).first()


def get_by_quiz(db: Session, quiz_id: int) -> List[Card]:
    """Lấy tất cả thẻ của một quiz, sắp xếp theo order_index."""
    return (
        db.query(Card)
        .filter(Card.quiz_id == quiz_id)
        .order_by(Card.order_index, Card.id)
        .all()
    )


def get_all_cards(db: Session) -> List[Card]:
    """Lấy toàn bộ thẻ của hệ thống theo thứ tự cố định."""
    return db.query(Card).order_by(Card.quiz_id, Card.order_index, Card.id).all()


def get_by_quiz_with_priority(
    db: Session, quiz_id: int, user_id: int
) -> List[Dict[str, Any]]:
    """
    Lấy thẻ của quiz kèm priority theo user (wrong - correct), sắp xếp giảm dần.
    Dùng raw SQL để JOIN hiệu quả.
    """
    sql = text("""
        SELECT
            c.id, c.quiz_id, c.vietnamese, c.pinyin, c.hanzi, c.order_index, c.audio_url, c.created_at,
            COALESCE(s.correct_count, 0) AS correct_count,
            COALESCE(s.wrong_count, 0)   AS wrong_count,
            COALESCE(s.wrong_count, 0) - COALESCE(s.correct_count, 0) AS priority
        FROM cards c
        LEFT JOIN user_card_stats s ON s.card_id = c.id AND s.user_id = :user_id
        WHERE c.quiz_id = :quiz_id
        ORDER BY priority DESC, c.order_index ASC
    """)
    rows = db.execute(sql, {"quiz_id": quiz_id, "user_id": user_id}).mappings().all()
    return [dict(row) for row in rows]


def get_all_with_priority(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Lấy toàn bộ thẻ hệ thống kèm priority theo user.
    Dùng cho chế độ 'Tất cả thẻ'.
    """
    sql = text("""
        SELECT
            c.id, c.quiz_id, c.vietnamese, c.pinyin, c.hanzi, c.order_index, c.audio_url, c.created_at,
            COALESCE(s.correct_count, 0) AS correct_count,
            COALESCE(s.wrong_count, 0)   AS wrong_count,
            COALESCE(s.wrong_count, 0) - COALESCE(s.correct_count, 0) AS priority
        FROM cards c
        LEFT JOIN user_card_stats s ON s.card_id = c.id AND s.user_id = :user_id
        ORDER BY priority DESC, c.quiz_id ASC, c.order_index ASC
    """)
    rows = db.execute(sql, {"user_id": user_id}).mappings().all()
    return [dict(row) for row in rows]


def create(
    db: Session,
    quiz_id: int,
    vietnamese: str,
    pinyin: str,
    hanzi: str,
    order_index: int = 0,
) -> Optional[Card]:
    """Tạo 1 thẻ mới."""
    try:
        db_card = Card(
            quiz_id=quiz_id,
            vietnamese=vietnamese,
            pinyin=pinyin,
            hanzi=hanzi,
            order_index=order_index,
        )
        db.add(db_card)
        db.commit()
        db.refresh(db_card)
        return db_card
    except Exception as e:
        db.rollback()
        raise e


def bulk_create(db: Session, cards_data: List[Dict[str, Any]]) -> List[Card]:
    """
    Tạo nhiều thẻ cùng lúc (Bulk Insert).
    cards_data: list of dict với keys: quiz_id, vietnamese, pinyin, hanzi, order_index.
    Trả về danh sách đối tượng Card đã lưu (có ID).
    """
    try:
        cards = [Card(**d) for d in cards_data]
        db.add_all(cards)
        db.commit()
        for c in cards:
            db.refresh(c)
        return cards
    except Exception as e:
        db.rollback()
        raise e


def update(db: Session, card: Card, **fields) -> Optional[Card]:
    """Cập nhật thẻ."""
    try:
        for key, value in fields.items():
            if value is not None and hasattr(card, key):
                setattr(card, key, value)
        db.commit()
        db.refresh(card)
        return card
    except Exception as e:
        db.rollback()
        raise e


def delete(db: Session, card: Card) -> bool:
    """Xóa thẻ và dọn dẹp file âm thanh tương ứng."""
    try:
        audio_url = card.audio_url
        db.delete(card)
        db.commit()
        if audio_url:
            from app.services.voice_service import delete_audio_file
            delete_audio_file(db, audio_url)
        return True
    except Exception as e:
        db.rollback()
        raise e


def delete_by_quiz(db: Session, quiz_id: int) -> int:
    """Xóa tất cả thẻ của 1 quiz (dùng khi re-import Excel) và dọn file âm thanh."""
    try:
        cards_audio = [
            r[0]
            for r in db.query(Card.audio_url)
            .filter(Card.quiz_id == quiz_id, Card.audio_url.isnot(None))
            .all()
            if r[0]
        ]
        count = db.query(Card).filter(Card.quiz_id == quiz_id).delete()
        db.commit()
        if cards_audio:
            from app.services.voice_service import delete_audio_files
            delete_audio_files(db, cards_audio)
        return count
    except Exception as e:
        db.rollback()
        raise e


def bulk_delete(db: Session, card_ids: List[int]) -> int:
    """Xóa nhiều thẻ theo danh sách card_ids và dọn file âm thanh."""
    try:
        cards_audio = [
            r[0]
            for r in db.query(Card.audio_url)
            .filter(Card.id.in_(card_ids), Card.audio_url.isnot(None))
            .all()
            if r[0]
        ]
        count = db.query(Card).filter(Card.id.in_(card_ids)).delete(synchronize_session=False)
        db.commit()
        if cards_audio:
            from app.services.voice_service import delete_audio_files
            delete_audio_files(db, cards_audio)
        return count
    except Exception as e:
        db.rollback()
        raise e


