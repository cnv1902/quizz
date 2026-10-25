import json
import random
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional

from app.dependencies import get_db, get_current_admin, get_current_user_optional
from app.models.user import User
from app.models.user_sentence_stat import UserSentenceStat
from app.schemas.sentence import (
    SentenceCreate,
    SentenceUpdate,
    SentenceResponse,
    SentencePuzzleItem,
    SentenceBulkCreateRequest,
    SentenceBulkDeleteRequest,
    SentenceProgressBatch,
)
from app.services import sentence_service, voice_service

router = APIRouter(prefix="/sentences", tags=["Sentences Puzzle Game"])


# === Public Endpoints (Dành cho Người chơi & Khách) ===

@router.get("", response_model=List[SentencePuzzleItem])
def get_puzzle_sentences(
    round: Optional[int] = Query(1, description="Màn chơi (bắt đầu từ 1)"),
    cards: Optional[str] = Query(None, description="Số câu mỗi màn (vd: 10, 15, 'all')"),
    priority: Optional[bool] = Query(False, description="Chế độ Luyện tập (xáo trộn ngẫu nhiên)"),
    set_id: Optional[int] = Query(None, description="Lọc theo ID của Bộ câu"),
    limit: Optional[int] = Query(None, description="Giới hạn số câu"),
    db: Session = Depends(get_db),
):
    """
    Lấy danh sách câu đố cho trò chơi Ghép câu theo màn chơi, bộ câu và số câu cấu hình.
    """
    sentences = sentence_service.get_all(db, set_id=set_id)
    if not sentences:
        return []

    # Nếu là chế độ Luyện tập: xáo trộn ngẫu nhiên toàn bộ câu
    if priority:
        selected = list(sentences)
        random.shuffle(selected)
        if cards and str(cards).strip().lower() != "all":
            try:
                k = max(1, int(cards))
                selected = selected[:k]
            except Exception:
                pass
    elif cards:
        if str(cards).strip().lower() == "all":
            selected = list(sentences)
        else:
            try:
                k = max(1, int(cards))
                r = max(1, round or 1)
                start_idx = (r - 1) * k
                end_idx = start_idx + k
                sliced = sentences[start_idx:end_idx]
                if sliced:
                    selected = sliced
                else:
                    selected = sentences[:k]
            except Exception:
                pass
    elif limit and limit > 0:
        selected = selected[:limit]
    else:
        selected = list(sentences)

    items = []
    for s in selected:
        tok_list = []
        if s.tokens:
            try:
                tok_list = json.loads(s.tokens)
            except Exception:
                tok_list = sentence_service.segment_sentence(s.chinese)
        else:
            tok_list = sentence_service.segment_sentence(s.chinese)

        # Xáo trộn các token của câu
        shuffled = list(tok_list)
        # Đảm bảo nếu câu có từ 2 từ trở lên, cố gắng xáo trộn khác ban đầu
        if len(shuffled) > 1:
            for _ in range(5):
                random.shuffle(shuffled)
                if shuffled != tok_list:
                    break

        items.append(SentencePuzzleItem(
            id=s.id,
            set_id=s.set_id,
            chinese=s.chinese,
            vietnamese=s.vietnamese,
            pinyin=s.pinyin or sentence_service.get_pinyin_for_sentence(s.chinese),
            audio_url=s.audio_url,
            shuffled_tokens=shuffled,
            total_tokens=len(tok_list),
        ))

    return items


@router.get("/all", response_model=List[SentenceResponse])
def get_all_sentences(
    set_id: Optional[int] = Query(None, description="Lọc câu theo ID Bộ câu"),
    db: Session = Depends(get_db),
):
    """Lấy danh sách tất cả câu theo thứ tự ban đầu (hỗ trợ lọc theo bộ câu)."""
    items = sentence_service.get_all(db, set_id=set_id)
    results = []
    for item in items:
        tok_list = []
        if item.tokens:
            try:
                tok_list = json.loads(item.tokens)
            except Exception:
                tok_list = sentence_service.segment_sentence(item.chinese)
        resp = SentenceResponse.model_validate(item)
        resp.token_list = tok_list
        results.append(resp)
    return results


@router.post("/progress/batch", response_model=dict)
def sync_sentence_progress(
    batch: SentenceProgressBatch,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    [Public/Thành viên] Đồng bộ kết quả sau khi kết thúc trò chơi Ghép câu.
    Nếu là khách (chưa đăng nhập), trả về kết quả êm đẹp mà không lưu DB.
    """
    if not current_user or not batch.results:
        return {"synced": 0, "correct": 0, "wrong": 0}

    from datetime import datetime

    correct = 0
    wrong = 0
    for item in batch.results:
        stat = (
            db.query(UserSentenceStat)
            .filter(
                UserSentenceStat.user_id == current_user.id,
                UserSentenceStat.sentence_id == item.sentence_id,
            )
            .first()
        )
        if not stat:
            stat = UserSentenceStat(
                user_id=current_user.id,
                sentence_id=item.sentence_id,
                correct_count=0,
                wrong_count=0,
                priority=0,
            )
            db.add(stat)

        if item.is_correct:
            stat.correct_count += 1
            correct += 1
        else:
            stat.wrong_count += 1
            wrong += 1

        stat.priority = stat.wrong_count - stat.correct_count
        stat.last_played = datetime.utcnow()

    db.commit()
    return {
        "synced": len(batch.results),
        "correct": correct,
        "wrong": wrong,
        "set_id": batch.set_id,
    }


@router.get("/template")
@router.get("/admin/template")
def download_sample_template():
    """Tải file Excel mẫu câu ghép 2 cột (Tiếng Trung | Tiếng Việt)."""
    excel_bytes = sentence_service.generate_sample_excel_template()
    filename = "hanziquizz_ghep_cau_mau.xlsx"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Access-Control-Expose-Headers": "Content-Disposition",
    }
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


# === Admin Endpoints (Chỉ Quản trị viên) ===

@router.post("/admin", response_model=SentenceResponse, status_code=status.HTTP_201_CREATED)
def admin_create_sentence(
    payload: SentenceCreate,
    background_tasks: BackgroundTasks,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Thêm 1 câu ghép mới."""
    item = sentence_service.create(
        db,
        chinese=payload.chinese,
        vietnamese=payload.vietnamese,
        pinyin=payload.pinyin,
        tokens=payload.tokens,
        order_index=payload.order_index or 0,
        audio_url=payload.audio_url,
        set_id=payload.set_id,
    )
    background_tasks.add_task(voice_service.background_generate_voices_for_sentences, [item.id])
    resp = SentenceResponse.model_validate(item)
    if item.tokens:
        try:
            resp.token_list = json.loads(item.tokens)
        except Exception:
            resp.token_list = sentence_service.segment_sentence(item.chinese)
    return resp


@router.post("/admin/bulk", response_model=List[SentenceResponse], status_code=status.HTTP_201_CREATED)
def admin_bulk_create(
    payload: SentenceBulkCreateRequest,
    background_tasks: BackgroundTasks,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Nhập hàng loạt câu qua modal."""
    raw = [item.model_dump() for item in payload.items]
    items = sentence_service.bulk_create(db, raw, set_id=payload.set_id)
    if items:
        background_tasks.add_task(voice_service.background_generate_voices_for_sentences, [i.id for i in items])

    results = []
    for item in items:
        resp = SentenceResponse.model_validate(item)
        if item.tokens:
            try:
                resp.token_list = json.loads(item.tokens)
            except Exception:
                resp.token_list = sentence_service.segment_sentence(item.chinese)
        results.append(resp)
    return results


@router.post("/admin/import", response_model=dict)
@router.post("/admin/import-excel", response_model=dict)
async def admin_import_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Import câu từ file Excel (.xlsx) hoặc CSV (.csv) chuẩn 2 cột."""
    lower_name = (file.filename or "").lower()
    if not lower_name.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ hỗ trợ file Excel (.xlsx, .xls) hoặc file CSV (.csv)",
        )
    try:
        content = await file.read()
        items = sentence_service.import_from_file(db, file.filename, content)
        count = len(items) if isinstance(items, list) else items
        if isinstance(items, list) and items:
            background_tasks.add_task(voice_service.background_generate_voices_for_sentences, [i.id for i in items])
        return {"message": f"Đã import thành công {count} câu vào trò chơi Ghép câu", "count": count}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi đọc file: {str(e)}",
        )


@router.put("/admin/{sentence_id}", response_model=SentenceResponse)
def admin_update_sentence(
    sentence_id: int,
    payload: SentenceUpdate,
    background_tasks: BackgroundTasks,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Cập nhật thông tin câu."""
    updates = payload.model_dump(exclude_none=True)
    item = sentence_service.update(db, sentence_id, **updates)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu")
    if "chinese" in updates:
        background_tasks.add_task(voice_service.background_generate_voices_for_sentences, [item.id])
    resp = SentenceResponse.model_validate(item)
    if item.tokens:
        try:
            resp.token_list = json.loads(item.tokens)
        except Exception:
            resp.token_list = sentence_service.segment_sentence(item.chinese)
    return resp


@router.delete("/admin/{sentence_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_sentence(
    sentence_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Xóa 1 câu."""
    if not sentence_service.delete(db, sentence_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu")


@router.post("/admin/bulk-delete", response_model=dict)
def admin_bulk_delete(
    payload: SentenceBulkDeleteRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Xóa hàng loạt câu theo danh sách IDs."""
    deleted_count = sentence_service.bulk_delete(db, payload.ids)
    return {"message": f"Đã xóa thành công {deleted_count} câu", "deleted_count": deleted_count}
