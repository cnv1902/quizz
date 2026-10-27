from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    quizzes,
    cards,
    progress,
    users,
    measure_words,
    grammar_points,
    voice,
    sentences,
    sentence_sets,
    custom_speech,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(quizzes.router)
api_router.include_router(cards.router)
api_router.include_router(progress.router)
api_router.include_router(users.router)
api_router.include_router(measure_words.router)
api_router.include_router(grammar_points.router)
api_router.include_router(sentences.router)
api_router.include_router(sentence_sets.router)
api_router.include_router(voice.router)
api_router.include_router(custom_speech.router)
