from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional

from app.dependencies import get_db, get_current_user, get_current_admin, get_current_user_optional
from app.models.user import User
from app.schemas.quiz import QuizCreate, QuizUpdate, QuizResponse, QuizListResponse
from app.services import quiz_service, card_service, voice_service

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


# === Public endpoints (List Quizzes) ===

@router.get("", response_model=List[dict])
def list_quizzes(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Danh sách tất cả quiz đang active kèm số thẻ (hỗ trợ cả khách và user đã đăng nhập)."""
    return quiz_service.get_all_quizzes_with_count(db)


# === Admin endpoints (Đặt TRƯỚC route /{quiz_id} để tránh router conflict) ===

@router.get("/admin/all", response_model=List[dict])
def admin_list_quizzes(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Danh sách tất cả quiz kể cả inactive."""
    return quiz_service.get_all_quizzes_admin(db)


@router.get("/admin/template")
@router.get("/template")
def download_sample_template():
    """Tải file Excel mẫu (.xlsx) 3 cột chuẩn."""
    excel_bytes = card_service.generate_sample_excel_template()
    filename = "hanziquizz_mau_3cot.xlsx"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.post("/admin", response_model=dict, status_code=status.HTTP_201_CREATED)
def admin_create_quiz(
    quiz_data: QuizCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Tạo quiz mới."""
    quiz = quiz_service.create_quiz(
        db,
        title=quiz_data.title,
        description=quiz_data.description,
        created_by=admin.id,
    )
    return {"id": quiz.id, "title": quiz.title, "description": quiz.description}


@router.post("/admin/{quiz_id}/import", response_model=dict)
async def admin_import_cards(
    quiz_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Import thẻ từ file Excel (.xlsx, .xls) hoặc CSV (.csv). Cột A=Tiếng Việt, B=Pinyin, C=Chữ Hán."""
    lower_name = (file.filename or "").lower()
    if not lower_name.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ hỗ trợ file Excel (.xlsx, .xls) hoặc file CSV (.csv)",
        )
    try:
        file_bytes = await file.read()
        created_cards = card_service.import_from_file(db, quiz_id, file.filename, file_bytes)
        count = len(created_cards) if isinstance(created_cards, list) else created_cards
        if isinstance(created_cards, list) and created_cards:
            background_tasks.add_task(
                voice_service.background_generate_voices_for_cards,
                [c.id for c in created_cards],
            )
        return {"message": f"Đã import thành công {count} thẻ", "count": count}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi đọc file: {str(e)}",
        )


@router.put("/admin/{quiz_id}", response_model=dict)
def admin_update_quiz(
    quiz_id: int,
    quiz_data: QuizUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Cập nhật quiz."""
    updates = quiz_data.model_dump(exclude_none=True)
    quiz = quiz_service.update_quiz(db, quiz_id, **updates)
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz không tồn tại")
    return {"id": quiz.id, "title": quiz.title, "is_active": quiz.is_active}


@router.delete("/admin/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_quiz(
    quiz_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Xóa quiz và tất cả thẻ liên quan."""
    if not quiz_service.delete_quiz(db, quiz_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz không tồn tại")


# === Dynamic quiz_id endpoints ===

@router.get("/{quiz_id}", response_model=dict)
def get_quiz(
    quiz_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Chi tiết quiz theo ID (hỗ trợ cả khách và user)."""
    quiz = quiz_service.get_quiz_detail(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz không tồn tại")
    return quiz


@router.get("/{quiz_id}/cards", response_model=List[dict])
def get_quiz_cards(
    quiz_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Lấy tất cả thẻ của quiz theo thứ tự thông thường (hỗ trợ cả khách và user)."""
    from app.crud import crud_quiz as cq
    quiz = cq.get_by_id(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz không tồn tại")
    cards = card_service.get_cards_for_quiz(db, quiz_id)
    return [
        {
            "id": c.id,
            "quiz_id": c.quiz_id,
            "vietnamese": c.vietnamese,
            "pinyin": c.pinyin,
            "hanzi": c.hanzi,
            "audio_url": c.audio_url,
            "audio_vi_url": getattr(c, "audio_vi_url", None),
            "order_index": c.order_index,
        }
        for c in cards
    ]


@router.get("/{quiz_id}/cards/priority", response_model=List[dict])
def get_quiz_cards_priority(
    quiz_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Lấy thẻ của quiz sắp xếp theo priority (Bổ Túc mode). Nếu khách thì trả về thẻ bình thường."""
    from app.crud import crud_quiz as cq
    quiz = cq.get_by_id(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz không tồn tại")
    if current_user:
        return card_service.get_cards_priority(db, quiz_id, current_user.id)
    cards = card_service.get_cards_for_quiz(db, quiz_id)
    return [
        {
            "id": c.id,
            "quiz_id": c.quiz_id,
            "vietnamese": c.vietnamese,
            "pinyin": c.pinyin,
            "hanzi": c.hanzi,
            "audio_url": c.audio_url,
            "audio_vi_url": getattr(c, "audio_vi_url", None),
            "order_index": c.order_index,
        }
        for c in cards
    ]
