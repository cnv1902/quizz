from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

db_url = settings.effective_database_url
connect_args = {}
engine_kwargs = {
    "echo": settings.SQL_ECHO,
}

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # Cấu hình tối ưu cho PostgreSQL / Supabase
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(
    db_url,
    connect_args=connect_args,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Tạo tất cả bảng trong database nếu chưa tồn tại (tự động tạo schema trên Supabase)."""
    from app.models.base import Base
    # Import tất cả models để SQLAlchemy nhận diện
    import app.models.user               # noqa: F401
    import app.models.quiz               # noqa: F401
    import app.models.card               # noqa: F401
    import app.models.user_card_stat     # noqa: F401
    import app.models.measure_word       # noqa: F401
    import app.models.grammar_point      # noqa: F401
    import app.models.sentence_set       # noqa: F401
    import app.models.sentence           # noqa: F401
    import app.models.user_sentence_stat # noqa: F401
    Base.metadata.create_all(bind=engine)
