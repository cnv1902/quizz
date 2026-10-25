from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.grammar_point import GrammarPoint


def get_all(db: Session) -> List[GrammarPoint]:
    """Lấy danh sách tất cả điểm ngữ pháp, sắp xếp theo order_index."""
    return db.query(GrammarPoint).order_by(GrammarPoint.order_index.asc(), GrammarPoint.id.asc()).all()


def get_by_id(db: Session, item_id: int) -> Optional[GrammarPoint]:
    """Lấy điểm ngữ pháp theo ID."""
    return db.query(GrammarPoint).filter(GrammarPoint.id == item_id).first()


def create(
    db: Session,
    vietnamese: str,
    pinyin: str,
    hanzi: str,
    order_index: int = 0,
) -> GrammarPoint:
    """Tạo điểm ngữ pháp mới."""
    item = GrammarPoint(
        vietnamese=vietnamese.strip(),
        pinyin=pinyin.strip(),
        hanzi=hanzi.strip(),
        order_index=order_index,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def bulk_create(db: Session, items: List[dict]) -> List[GrammarPoint]:
    """Tạo nhiều điểm ngữ pháp cùng lúc."""
    created = []
    max_order = db.query(GrammarPoint).count()
    for idx, d in enumerate(items):
        item = GrammarPoint(
            vietnamese=d["vietnamese"].strip(),
            pinyin=d["pinyin"].strip(),
            hanzi=d["hanzi"].strip(),
            order_index=d.get("order_index", max_order + idx + 1),
        )
        db.add(item)
        created.append(item)
    db.commit()
    for c in created:
        db.refresh(c)
    return created


def update(db: Session, item_id: int, **kwargs) -> Optional[GrammarPoint]:
    """Cập nhật thông tin điểm ngữ pháp."""
    item = get_by_id(db, item_id)
    if not item:
        return None
    for k, v in kwargs.items():
        if hasattr(item, k) and v is not None:
            setattr(item, k, v.strip() if isinstance(v, str) else v)
    db.commit()
    db.refresh(item)
    return item


def delete(db: Session, item_id: int) -> bool:
    """Xóa 1 điểm ngữ pháp."""
    item = get_by_id(db, item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def bulk_delete(db: Session, ids: List[int]) -> int:
    """Xóa hàng loạt điểm ngữ pháp theo danh sách IDs."""
    if not ids:
        return 0
    deleted = db.query(GrammarPoint).filter(GrammarPoint.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return deleted
