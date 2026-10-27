from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Any
import os

from app.database import SessionLocal
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.custom_speech import CustomSpeechArticle
from app.services.custom_speech_service import (
    segment_bilingual_text,
    synthesize_and_stitch_article,
    BASE_DIR,
)

router = APIRouter(prefix="/custom-speech", tags=["Custom Speech"])


class ArticleCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Tiêu đề bài viết")
    content: str = Field(..., min_length=1, description="Đoạn văn bản song ngữ Trung - Việt")


class SegmentItem(BaseModel):
    id: int
    text: str
    lang: str
    start_time: float
    end_time: float


class ArticleResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    audio_url: str
    duration_seconds: float
    segments: List[Any]
    created_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[ArticleResponse])
def get_my_articles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lấy danh sách tất cả bài viết của user đang đăng nhập.
    Bảo mật tuyệt đối: Chỉ lấy dữ liệu gắn liền với current_user.id.
    """
    articles = (
        db.query(CustomSpeechArticle)
        .filter(CustomSpeechArticle.user_id == current_user.id)
        .order_by(CustomSpeechArticle.created_at.desc())
        .all()
    )
    return [
        ArticleResponse(
            id=a.id,
            user_id=a.user_id,
            title=a.title,
            content=a.content,
            audio_url=a.audio_url,
            duration_seconds=a.duration_seconds,
            segments=a.segments or [],
            created_at=a.created_at.strftime("%d/%m/%Y %H:%M"),
        )
        for a in articles
    ]


@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    payload: ArticleCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Tạo bài viết mới:
    1. Tự động nhận diện chữ Hán (zh) và Tiếng Việt (vi).
    2. Sinh giọng đọc Edge-TTS tương ứng cho từng đoạn.
    3. Ghép thành DUY NHẤT 1 FILE MP3 từ đầu đến cuối kèm mốc thời gian Karaoke.
    4. Chỉ người dùng đã đăng nhập mới được gọi API này.
    """
    clean_title = payload.title.strip()
    clean_content = payload.content.strip()

    if not clean_title:
        raise HTTPException(status_code=400, detail="Tiêu đề không được để trống")
    if not clean_content:
        raise HTTPException(status_code=400, detail="Nội dung không được để trống")

    # 1. Bóc tách ngôn ngữ
    segments = segment_bilingual_text(clean_content)
    if not segments:
        raise HTTPException(status_code=400, detail="Không tìm thấy nội dung hợp lệ để phát âm thanh")

    # 2. Tạo bản ghi ban đầu trong database
    article = CustomSpeechArticle(
        user_id=current_user.id,
        title=clean_title,
        content=clean_content,
        audio_url="",
        duration_seconds=0.0,
        segments=[],
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    # 3. Sinh âm thanh và ghép thành 1 file MP3
    try:
        audio_url, duration, updated_segments = await synthesize_and_stitch_article(
            article_id=article.id,
            user_id=current_user.id,
            segments=segments,
        )
        article.audio_url = audio_url
        article.duration_seconds = duration
        article.segments = updated_segments
        db.commit()
        db.refresh(article)
    except Exception as e:
        db.delete(article)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Lỗi sinh âm thanh bài viết: {str(e)}")

    return ArticleResponse(
        id=article.id,
        user_id=article.user_id,
        title=article.title,
        content=article.content,
        audio_url=article.audio_url,
        duration_seconds=article.duration_seconds,
        segments=article.segments,
        created_at=article.created_at.strftime("%d/%m/%Y %H:%M"),
    )


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article_detail(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lấy chi tiết 1 bài viết kèm mốc thời gian Karaoke để nạp vào trình phát.
    Bảo mật: Chỉ chủ sở hữu (user_id khớp) mới được truy cập.
    """
    article = (
        db.query(CustomSpeechArticle)
        .filter(
            CustomSpeechArticle.id == article_id,
            CustomSpeechArticle.user_id == current_user.id,
        )
        .first()
    )
    if not article:
        raise HTTPException(status_code=404, detail="Bài viết không tồn tại hoặc bạn không có quyền truy cập")

    return ArticleResponse(
        id=article.id,
        user_id=article.user_id,
        title=article.title,
        content=article.content,
        audio_url=article.audio_url,
        duration_seconds=article.duration_seconds,
        segments=article.segments or [],
        created_at=article.created_at.strftime("%d/%m/%Y %H:%M"),
    )


@router.delete("/{article_id}", status_code=status.HTTP_200_OK)
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Xóa bài viết và dọn dẹp file MP3 vật lý trên máy chủ.
    """
    article = (
        db.query(CustomSpeechArticle)
        .filter(
            CustomSpeechArticle.id == article_id,
            CustomSpeechArticle.user_id == current_user.id,
        )
        .first()
    )
    if not article:
        raise HTTPException(status_code=404, detail="Bài viết không tồn tại hoặc bạn không có quyền xóa")

    # Dọn dẹp file MP3 vật lý
    if article.audio_url:
        try:
            rel = article.audio_url.lstrip("/\\")
            abs_path = os.path.join(BASE_DIR, rel)
            if os.path.exists(abs_path):
                os.remove(abs_path)
        except Exception as e:
            print(f"[CustomSpeech] Không thể xóa file mp3: {e}")

    db.delete(article)
    db.commit()
    return {"message": "Đã xóa bài viết thành công"}
