from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db, get_current_admin
from app.models.user import User
from app.schemas.measure_word import (
    MeasureWordCreate,
    MeasureWordUpdate,
    MeasureWordResponse,
    MeasureWordBulkCreateRequest,
    MeasureWordBulkDeleteRequest,
)
from app.services import measure_word_service, voice_service

router = APIRouter(prefix="/measure-words", tags=["Measure Words"])


# === Public Endpoints (Khách & User đều đọc được) ===

@router.get("", response_model=List[MeasureWordResponse])
def get_all_measure_words(db: Session = Depends(get_db)):
    """Lấy toàn bộ danh sách lượng từ theo thứ tự order_index (Không cần đăng nhập)."""
    return measure_word_service.get_all(db)


@router.get("/template")
@router.get("/admin/template")
def download_sample_template():
    """Tải file Excel mẫu lượng từ 3 cột (Tiếng Việt | Pinyin | Chữ Hán)."""
    excel_bytes = measure_word_service.generate_sample_excel_template()
    filename = "hanziquizz_luongtu_mau.xlsx"
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


@router.post("/admin", response_model=MeasureWordResponse, status_code=status.HTTP_201_CREATED)
def admin_create_measure_word(
    payload: MeasureWordCreate,
    background_tasks: BackgroundTasks,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Thêm 1 lượng từ mới."""
    item = measure_word_service.create(
        db,
        vietnamese=payload.vietnamese,
        pinyin=payload.pinyin,
        hanzi=payload.hanzi,
        order_index=payload.order_index or 0,
    )
    background_tasks.add_task(voice_service.background_generate_voices_for_measure_words, [item.id])
    return item


@router.post("/admin/bulk", response_model=List[MeasureWordResponse], status_code=status.HTTP_201_CREATED)
def admin_bulk_create(
    payload: MeasureWordBulkCreateRequest,
    background_tasks: BackgroundTasks,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Nhập hàng loạt lượng từ qua modal."""
    raw = [item.model_dump() for item in payload.items]
    items = measure_word_service.bulk_create(db, raw)
    if items:
        background_tasks.add_task(voice_service.background_generate_voices_for_measure_words, [i.id for i in items])
    return items


@router.post("/admin/import", response_model=dict)
@router.post("/admin/import-excel", response_model=dict)
async def admin_import_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Import lượng từ từ file Excel (.xlsx) hoặc CSV (.csv)."""
    lower_name = (file.filename or "").lower()
    if not lower_name.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ hỗ trợ file Excel (.xlsx, .xls) hoặc file CSV (.csv)",
        )
    try:
        content = await file.read()
        items = measure_word_service.import_from_file(db, file.filename, content)
        count = len(items) if isinstance(items, list) else items
        if isinstance(items, list) and items:
            background_tasks.add_task(voice_service.background_generate_voices_for_measure_words, [i.id for i in items])
        return {"message": f"Đã import thành công {count} lượng từ", "count": count}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi đọc file: {str(e)}",
        )


@router.put("/admin/{item_id}", response_model=MeasureWordResponse)
def admin_update_measure_word(
    item_id: int,
    payload: MeasureWordUpdate,
    background_tasks: BackgroundTasks,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Cập nhật lượng từ."""
    updates = payload.model_dump(exclude_none=True)
    item = measure_word_service.update(db, item_id, **updates)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lượng từ")
    if "hanzi" in updates:
        background_tasks.add_task(voice_service.background_generate_voices_for_measure_words, [item.id])
    return item


@router.delete("/admin/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_measure_word(
    item_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Xóa 1 lượng từ."""
    if not measure_word_service.delete(db, item_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lượng từ")


@router.post("/admin/bulk-delete", response_model=dict)
def admin_bulk_delete(
    payload: MeasureWordBulkDeleteRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Xóa hàng loạt lượng từ theo danh sách IDs."""
    count = measure_word_service.bulk_delete(db, payload.ids)
    return {"message": f"Đã xóa thành công {count} lượng từ", "count": count}
