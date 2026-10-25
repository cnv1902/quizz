from typing import List
from sqlalchemy.orm import Session
from app.crud import crud_progress
from app.schemas.progress import ProgressBatch, QuizProgressResponse


def sync_game_results(db: Session, user_id: int, batch: ProgressBatch) -> dict:
    """
    Xử lý batch kết quả sau khi kết thúc game.
    Cập nhật correct_count, wrong_count, priority cho mỗi thẻ.
    Trả về summary của batch đã xử lý.
    """
    results = [
        {"card_id": item.card_id, "is_correct": item.is_correct}
        for item in batch.results
    ]
    crud_progress.batch_update(db, user_id, results)

    correct = sum(1 for r in batch.results if r.is_correct)
    wrong = sum(1 for r in batch.results if not r.is_correct)

    return {
        "synced": len(results),
        "correct": correct,
        "wrong": wrong,
        "game_type": batch.game_type,
    }


def get_quiz_progress(db: Session, user_id: int, quiz_id: int) -> QuizProgressResponse:
    """Lấy thống kê tiến độ của user trong 1 quiz."""
    stats = crud_progress.get_quiz_stats(db, user_id, quiz_id)
    return QuizProgressResponse(**stats)
