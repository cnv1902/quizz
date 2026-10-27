from pydantic import BaseModel
from typing import List, Optional


class ProgressItem(BaseModel):
    """Kết quả 1 thẻ trong 1 màn chơi."""
    card_id: int
    is_correct: bool


class ProgressBatch(BaseModel):
    """Schema gửi batch kết quả sau khi kết thúc game."""
    results: List[ProgressItem]
    game_type: str  # "flashcard", "pikachu", "multiple_choice", "fill_in"
    quiz_id: Optional[int] = None  # None nếu là chế độ "tất cả thẻ"


class CardStatResponse(BaseModel):
    """Thống kê của 1 thẻ theo user."""
    card_id: int
    correct_count: int
    wrong_count: int
    priority: int

    model_config = {"from_attributes": True}


class QuizProgressResponse(BaseModel):
    """Tổng quan tiến độ của user trong 1 quiz."""
    quiz_id: int
    total_cards: int
    cards_studied: int
    total_correct: int
    total_wrong: int
    average_priority: float


class UserProgressSummary(BaseModel):
    """Tổng quan tiến độ trang chủ cho user."""
    streak: int
    mastered_cards: int
    review_needed: int
    total_cards: int

