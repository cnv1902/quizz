from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_admin
from app.models.user import User
from app.services import voice_service

router = APIRouter(prefix="/voice", tags=["Voice Service"])


@router.post("/admin/sync-all", response_model=dict)
def admin_sync_all_voices(
    background_tasks: BackgroundTasks,
    admin: User = Depends(get_current_admin),
):
    """
    [Admin] Kích hoạt tiến trình nền quét toàn bộ hệ thống
    và tự động sinh file âm thanh chuẩn HSK cho các thẻ, lượng từ, ngữ pháp chưa có audio.
    """
    background_tasks.add_task(voice_service.sync_all_missing_voices)
    return {
        "message": "Đã bắt đầu tiến trình nền đồng bộ và tạo voice chuẩn HSK cho toàn hệ thống.",
        "status": "processing",
    }
