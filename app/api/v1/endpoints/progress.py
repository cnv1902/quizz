from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies import get_db, get_current_user, get_current_user_optional
from app.models.user import User
from app.schemas.progress import ProgressBatch, QuizProgressResponse
from app.services import progress_service

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.post("/batch", response_model=dict)
def sync_progress(
    batch: ProgressBatch,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Background sync: nhận batch kết quả sau khi kết thúc game.
    Nếu chưa đăng nhập (khách), bỏ qua sync êm đẹp.
    """
    if not current_user or not batch.results:
        return {"synced": 0, "correct": 0, "wrong": 0}
    result = progress_service.sync_game_results(db, current_user.id, batch)
    return result


@router.get("/stats/{quiz_id}", response_model=QuizProgressResponse)
def get_quiz_stats(
    quiz_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Thống kê tiến độ của user trong quiz. Nếu là khách thì trả về 0."""
    if not current_user:
        return QuizProgressResponse(
            quiz_id=quiz_id,
            total_cards=0,
            learned_cards=0,
            accuracy_rate=0.0,
        )
    return progress_service.get_quiz_progress(db, current_user.id, quiz_id)
