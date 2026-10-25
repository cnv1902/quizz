from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
import re

from app.models.sentence_set import SentenceSet
from app.models.sentence import Sentence
from app.services import sentence_service


def get_all_with_count(db: Session) -> List[Dict[str, Any]]:
    """Lấy danh sách các bộ câu đang active kèm số lượng câu và mẫu chữ Hán."""
    sets = db.query(SentenceSet).filter(SentenceSet.is_active == True).order_by(SentenceSet.order_index, SentenceSet.id).all()
    results = []
    for s in sets:
        count = db.query(func.count(Sentence.id)).filter(Sentence.set_id == s.id).scalar() or 0
        
        # Lấy mẫu chữ Hán từ 1 câu đầu tiên
        first_sentence = db.query(Sentence).filter(Sentence.set_id == s.id).first()
        samples = "你 · 好 · 吗 · ？"
        if first_sentence and first_sentence.chinese:
            clean_han = re.sub(r"[^\u4e00-\u9fff]", "", first_sentence.chinese)
            if len(clean_han) >= 4:
                samples = " · ".join(list(clean_han[:4]))
            elif clean_han:
                samples = " · ".join(list(clean_han))

        results.append({
            "id": s.id,
            "title": s.title,
            "description": s.description or "",
            "is_active": s.is_active,
            "sentence_count": count,
            "samples": samples,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })
    return results


def get_all_admin(db: Session) -> List[Dict[str, Any]]:
    """[Admin] Lấy danh sách tất cả các bộ câu kể cả inactive."""
    sets = db.query(SentenceSet).order_by(SentenceSet.order_index, SentenceSet.id.desc()).all()
    results = []
    for s in sets:
        count = db.query(func.count(Sentence.id)).filter(Sentence.set_id == s.id).scalar() or 0
        results.append({
            "id": s.id,
            "title": s.title,
            "description": s.description or "",
            "is_active": s.is_active,
            "order_index": s.order_index,
            "sentence_count": count,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })
    return results


def get_by_id(db: Session, set_id: int) -> Optional[SentenceSet]:
    """Lấy chi tiết bộ câu theo ID."""
    return db.query(SentenceSet).filter(SentenceSet.id == set_id).first()


def create(
    db: Session,
    title: str,
    description: Optional[str] = None,
    created_by: Optional[int] = None,
    is_active: bool = True,
    order_index: int = 0,
) -> SentenceSet:
    """[Admin] Tạo bộ câu mới."""
    new_set = SentenceSet(
        title=title.strip(),
        description=description.strip() if description else None,
        created_by=created_by,
        is_active=is_active,
        order_index=order_index,
    )
    db.add(new_set)
    db.commit()
    db.refresh(new_set)
    return new_set


def update(db: Session, set_id: int, **kwargs) -> Optional[SentenceSet]:
    """[Admin] Cập nhật bộ câu."""
    target_set = get_by_id(db, set_id)
    if not target_set:
        return None
    for k, v in kwargs.items():
        if hasattr(target_set, k) and v is not None:
            setattr(target_set, k, v)
    db.commit()
    db.refresh(target_set)
    return target_set


def delete(db: Session, set_id: int) -> bool:
    """[Admin] Xóa bộ câu (các câu thuộc bộ câu sẽ tự động bị xóa cascade)."""
    target_set = get_by_id(db, set_id)
    if not target_set:
        return False
    db.delete(target_set)
    db.commit()
    return True


def get_sentences_by_set(db: Session, set_id: int) -> List[Sentence]:
    """Lấy tất cả các câu thuộc về một bộ câu."""
    return db.query(Sentence).filter(Sentence.set_id == set_id).order_by(Sentence.order_index, Sentence.id).all()


def import_to_set(db: Session, set_id: int, filename: str, file_bytes: bytes) -> List[Sentence]:
    """[Admin] Import file Excel vào trực tiếp bộ câu được chỉ định."""
    target_set = get_by_id(db, set_id)
    if not target_set:
        raise ValueError("Không tìm thấy bộ câu được chỉ định")
    
    # Dùng sentence_service.import_from_file có hỗ trợ gán set_id
    return sentence_service.import_from_file(db, filename, file_bytes, set_id=set_id)
