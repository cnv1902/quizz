from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.dependencies import get_db, get_current_admin, get_current_user_optional
from app.models.user import User
from app.schemas.sentence_set import SentenceSetCreate, SentenceSetUpdate, SentenceSetResponse
from app.schemas.sentence import SentenceResponse
from app.services import sentence_set_service, voice_service

router = APIRouter(prefix="/sentence-sets", tags=["Sentence Sets"])


# === Public Endpoints ===

@router.get("", response_model=List[dict])
def list_sentence_sets(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Lấy danh sách các bộ câu ghép đang kích hoạt kèm số lượng câu và mẫu hiển thị."""
    return sentence_set_service.get_all_with_count(db)


# === Admin Endpoints (Đặt trước route /{set_id} để tránh conflict) ===

@router.get("/admin/all", response_model=List[dict])
def admin_list_sentence_sets(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Danh sách tất cả bộ câu kể cả inactive."""
    return sentence_set_service.get_all_admin(db)


@router.post("/admin", response_model=dict, status_code=status.HTTP_201_CREATED)
def admin_create_sentence_set(
    set_data: SentenceSetCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Tạo bộ câu mới."""
    new_set = sentence_set_service.create(
        db,
        title=set_data.title,
        description=set_data.description,
        created_by=admin.id,
        is_active=set_data.is_active,
        order_index=set_data.order_index,
    )
    return {
        "id": new_set.id,
        "title": new_set.title,
        "description": new_set.description,
        "is_active": new_set.is_active,
    }


@router.post("/admin/{set_id}/import", response_model=dict)
async def admin_import_sentences(
    set_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Import câu từ file Excel (.xlsx, .xls) hoặc CSV vào bộ câu này."""
    lower_name = (file.filename or "").lower()
    if not lower_name.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File không hợp lệ. Vui lòng chọn file .xlsx, .xls hoặc .csv",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File rỗng, vui lòng chọn file có dữ liệu",
        )

    try:
        created = sentence_set_service.import_to_set(db, set_id, file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi import file: {str(e)}",
        )

    # Sinh voice MP3 tự động ngầm
    if created:
        background_tasks.add_task(
            voice_service.background_generate_voices_for_sentences,
            [s.id for s in created],
        )

    return {
        "message": f"Import thành công {len(created)} câu vào bộ câu!",
        "count": len(created),
    }


@router.put("/admin/{set_id}", response_model=dict)
def admin_update_sentence_set(
    set_id: int,
    set_data: SentenceSetUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Cập nhật thông tin bộ câu."""
    updated = sentence_set_service.update(
        db,
        set_id,
        title=set_data.title,
        description=set_data.description,
        is_active=set_data.is_active,
        order_index=set_data.order_index,
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bộ câu")
    return {"message": "Cập nhật bộ câu thành công", "id": updated.id, "title": updated.title}


@router.delete("/admin/{set_id}", response_model=dict)
def admin_delete_sentence_set(
    set_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Xóa bộ câu (các câu trong bộ cũng sẽ bị xóa)."""
    success = sentence_set_service.delete(db, set_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bộ câu")
    return {"message": "Đã xóa bộ câu thành công"}


# === Chi tiết bộ câu & danh sách câu thuộc bộ ===

@router.get("/{set_id}", response_model=dict)
def get_sentence_set_detail(
    set_id: int,
    db: Session = Depends(get_db),
):
    """Lấy chi tiết một bộ câu."""
    s = sentence_set_service.get_by_id(db, set_id)
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bộ câu")
    count = len(s.sentences) if s.sentences else 0
    return {
        "id": s.id,
        "title": s.title,
        "description": s.description or "",
        "is_active": s.is_active,
        "sentence_count": count,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


@router.get("/{set_id}/sentences", response_model=List[SentenceResponse])
def get_sentence_set_sentences(
    set_id: int,
    db: Session = Depends(get_db),
):
    """Lấy toàn bộ các câu thuộc về một bộ câu."""
    sentences = sentence_set_service.get_sentences_by_set(db, set_id)
    return sentences
