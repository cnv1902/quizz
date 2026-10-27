from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.sentence import Sentence


def get_all(db: Session, set_id: Optional[int] = None, skip: int = 0, limit: Optional[int] = None) -> List[Sentence]:
    """Lấy danh sách các câu, hỗ trợ lọc theo set_id, sắp xếp theo thứ tự order_index tăng dần."""
    query = db.query(Sentence)
    if set_id is not None:
        query = query.filter(Sentence.set_id == set_id)
    query = query.order_by(Sentence.order_index.asc(), Sentence.id.asc())
    if skip:
        query = query.offset(skip)
    if limit:
        query = query.limit(limit)
    return query.all()


def get_by_id(db: Session, sentence_id: int) -> Optional[Sentence]:
    """Lấy câu theo ID."""
    return db.query(Sentence).filter(Sentence.id == sentence_id).first()


def create(
    db: Session,
    chinese: str,
    vietnamese: str,
    pinyin: Optional[str] = None,
    tokens: Optional[str] = None,
    order_index: int = 0,
    audio_url: Optional[str] = None,
    audio_vi_url: Optional[str] = None,
    set_id: Optional[int] = None,
) -> Sentence:
    """Tạo câu mới."""
    item = Sentence(
        chinese=chinese.strip(),
        vietnamese=vietnamese.strip(),
        pinyin=pinyin.strip() if pinyin else None,
        tokens=tokens.strip() if tokens else None,
        order_index=order_index,
        audio_url=audio_url.strip() if audio_url else None,
        audio_vi_url=audio_vi_url.strip() if audio_vi_url else None,
        set_id=set_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def bulk_create(db: Session, items: List[dict], set_id: Optional[int] = None) -> List[Sentence]:
    """Tạo nhiều câu cùng lúc."""
    created = []
    base_query = db.query(Sentence)
    if set_id is not None:
        base_query = base_query.filter(Sentence.set_id == set_id)
    max_order = base_query.count()

    for idx, d in enumerate(items):
        item_set_id = d.get("set_id") if d.get("set_id") is not None else set_id
        item = Sentence(
            set_id=item_set_id,
            chinese=str(d.get("chinese") or "").strip(),
            vietnamese=str(d.get("vietnamese") or "").strip(),
            pinyin=str(d["pinyin"]).strip() if d.get("pinyin") else None,
            tokens=str(d["tokens"]).strip() if d.get("tokens") else None,
            order_index=d.get("order_index", max_order + idx + 1),
            audio_url=str(d["audio_url"]).strip() if d.get("audio_url") else None,
            audio_vi_url=str(d["audio_vi_url"]).strip() if d.get("audio_vi_url") else None,
        )
        db.add(item)
        created.append(item)
    db.commit()
    for c in created:
        db.refresh(c)
    return created


def update(db: Session, sentence_id: int, **kwargs) -> Optional[Sentence]:
    """Cập nhật thông tin câu."""
    item = get_by_id(db, sentence_id)
    if not item:
        return None
    for k, v in kwargs.items():
        if hasattr(item, k) and v is not None:
            setattr(item, k, v.strip() if isinstance(v, str) else v)
    db.commit()
    db.refresh(item)
    return item


def delete(db: Session, sentence_id: int) -> bool:
    """Xóa 1 câu và dọn dẹp file âm thanh tương ứng (Trung & Việt)."""
    item = get_by_id(db, sentence_id)
    if not item:
        return False
    urls_to_delete = [u for u in [item.audio_url, item.audio_vi_url] if u]
    db.delete(item)
    db.commit()
    if urls_to_delete:
        from app.services.voice_service import delete_audio_files
        delete_audio_files(db, urls_to_delete)
    return True


def bulk_delete(db: Session, ids: List[int]) -> int:
    """Xóa hàng loạt câu theo danh sách IDs và dọn dẹp file âm thanh (Trung & Việt)."""
    if not ids:
        return 0
    sentences_rows = (
        db.query(Sentence.audio_url, Sentence.audio_vi_url)
        .filter(Sentence.id.in_(ids))
        .all()
    )
    sentences_audio = []
    for r in sentences_rows:
        if r[0]: sentences_audio.append(r[0])
        if r[1]: sentences_audio.append(r[1])

    deleted = db.query(Sentence).filter(Sentence.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    if sentences_audio:
        from app.services.voice_service import delete_audio_files
        delete_audio_files(db, sentences_audio)
    return deleted


