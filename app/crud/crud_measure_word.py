from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.measure_word import MeasureWord


def get_all(db: Session) -> List[MeasureWord]:
    """Lấy danh sách tất cả lượng từ, sắp xếp theo order_index."""
    return db.query(MeasureWord).order_by(MeasureWord.order_index.asc(), MeasureWord.id.asc()).all()


def get_by_id(db: Session, item_id: int) -> Optional[MeasureWord]:
    """Lấy lượng từ theo ID."""
    return db.query(MeasureWord).filter(MeasureWord.id == item_id).first()


def create(
    db: Session,
    vietnamese: str,
    pinyin: str,
    hanzi: str,
    order_index: int = 0,
) -> MeasureWord:
    """Tạo lượng từ mới."""
    item = MeasureWord(
        vietnamese=vietnamese.strip(),
        pinyin=pinyin.strip(),
        hanzi=hanzi.strip(),
        order_index=order_index,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def bulk_create(db: Session, items: List[dict]) -> List[MeasureWord]:
    """Tạo nhiều lượng từ cùng lúc."""
    created = []
    max_order = db.query(MeasureWord).count()
    for idx, d in enumerate(items):
        item = MeasureWord(
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


def update(db: Session, item_id: int, **kwargs) -> Optional[MeasureWord]:
    """Cập nhật thông tin lượng từ."""
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
    """Xóa 1 lượng từ."""
    item = get_by_id(db, item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def bulk_delete(db: Session, ids: List[int]) -> int:
    """Xóa hàng loạt lượng từ theo danh sách IDs."""
    if not ids:
        return 0
    deleted = db.query(MeasureWord).filter(MeasureWord.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return deleted
