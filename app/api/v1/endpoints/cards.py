from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.dependencies import get_db, get_current_user, get_current_admin, get_current_user_optional
from app.models.user import User
from app.schemas.card import CardCreate, CardUpdate, CardBulkCreateRequest, CardBulkDeleteRequest
from app.services import card_service, voice_service
from app.crud import crud_card



router = APIRouter(prefix="/cards", tags=["Cards"])


@router.get("/all", response_model=List[dict])
def get_all_cards(
    priority: bool = False,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Lấy toàn bộ thẻ hệ thống:
    - Nếu priority=True và đã đăng nhập: sắp xếp theo priority của user (Bổ Túc / Luyện tập).
    - Ngược lại (chơi theo Màn thông thường): sắp xếp theo thứ tự cố định (quiz_id, order_index, id).
    """
    if priority and current_user:
        return card_service.get_all_cards_priority(db, current_user.id)
    cards = crud_card.get_all_cards(db)
    return [
        {
            "id": c.id,
            "quiz_id": c.quiz_id,
            "vietnamese": c.vietnamese,
            "pinyin": c.pinyin,
            "hanzi": c.hanzi,
            "audio_url": c.audio_url,
            "order_index": c.order_index,
        }
        for c in cards
    ]


# === Admin Card Management ===

@router.post("/admin", response_model=dict, status_code=status.HTTP_201_CREATED)
def admin_create_card(
    card_data: CardCreate,
    background_tasks: BackgroundTasks,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Tạo thẻ mới thủ công."""
    try:
        card = card_service.create_card(
            db,
            quiz_id=card_data.quiz_id,
            vietnamese=card_data.vietnamese,
            pinyin=card_data.pinyin,
            hanzi=card_data.hanzi,
            order_index=card_data.order_index,
        )
        background_tasks.add_task(voice_service.background_generate_voices_for_cards, [card.id])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {
        "id": card.id,
        "quiz_id": card.quiz_id,
        "vietnamese": card.vietnamese,
        "pinyin": card.pinyin,
        "hanzi": card.hanzi,
        "audio_url": card.audio_url,
        "order_index": card.order_index,
    }


@router.post("/admin/bulk", response_model=List[dict], status_code=status.HTTP_201_CREATED)
def admin_bulk_create_cards(
    payload: CardBulkCreateRequest,
    background_tasks: BackgroundTasks,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Nhập hàng loạt thẻ vào quiz."""
    try:
        created_cards = card_service.bulk_create_cards(
            db,
            quiz_id=payload.quiz_id,
            cards=[c.model_dump() for c in payload.cards],
        )
        card_ids = [c["id"] for c in created_cards if isinstance(c, dict) and "id" in c]
        if card_ids:
            background_tasks.add_task(voice_service.background_generate_voices_for_cards, card_ids)
        return created_cards
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/admin/{card_id}", response_model=dict)

def admin_update_card(
    card_id: int,
    card_data: CardUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Cập nhật thẻ."""
    updates = card_data.model_dump(exclude_none=True)
    card = card_service.update_card(db, card_id, **updates)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thẻ không tồn tại")
    return {
        "id": card.id,
        "quiz_id": card.quiz_id,
        "vietnamese": card.vietnamese,
        "pinyin": card.pinyin,
        "hanzi": card.hanzi,
        "order_index": card.order_index,
    }


@router.delete("/admin/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_card(
    card_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Xóa thẻ."""
    if not card_service.delete_card(db, card_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thẻ không tồn tại")


@router.post("/admin/bulk-delete", status_code=status.HTTP_200_OK)
def admin_bulk_delete_cards(
    payload: CardBulkDeleteRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Xóa hàng loạt thẻ theo danh sách card_ids."""
    count = card_service.delete_cards_bulk(db, payload.card_ids)
    return {"message": f"Đã xóa {count} thẻ thành công", "deleted_count": count}

