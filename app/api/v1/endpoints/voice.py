from fastapi import APIRouter, Depends, BackgroundTasks, Query, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_admin
from app.models.user import User
from app.services import voice_service
from app.services.voice_service import (
    generate_voice_file,
    DEFAULT_VOICE, DEFAULT_RATE,
    DEFAULT_VOICE_VI, DEFAULT_RATE_VI,
)

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


@router.get("/generate", response_model=dict)
async def generate_voice_on_demand(
    text: str = Query(..., min_length=1, max_length=2000, description="Văn bản cần đọc"),
    lang: str = Query("zh", description="Ngôn ngữ: 'zh' (tiếng Trung) hoặc 'vi' (tiếng Việt)"),
):
    """
    [Public] Sinh file MP3 Edge-TTS theo yêu cầu và trả về URL tĩnh.
    Frontend gọi endpoint này khi audio_url bị thiếu hoặc không load được,
    đảm bảo luôn phát đúng giọng Neural Edge-TTS thay vì rơi sang Web Speech API.
    """
    if lang not in ("zh", "vi"):
        raise HTTPException(status_code=400, detail="lang chỉ chấp nhận 'zh' hoặc 'vi'")

    clean_text = (text or "").strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Văn bản không được rỗng")

    if lang == "zh":
        category = "cards"
        voice = DEFAULT_VOICE
        rate = DEFAULT_RATE
    else:
        category = "cards_vi"
        voice = DEFAULT_VOICE_VI
        rate = DEFAULT_RATE_VI

    url = await generate_voice_file(clean_text, category=category, voice=voice, rate=rate)
    if not url:
        raise HTTPException(status_code=500, detail="Không thể sinh file âm thanh. Vui lòng thử lại.")

    return {"url": url, "lang": lang, "text": clean_text}
