from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# SQLite engine với WAL mode để hỗ trợ concurrent reads
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Bắt buộc cho SQLite
    echo=settings.SQL_ECHO,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Tạo tất cả bảng trong database nếu chưa tồn tại và seed dữ liệu khởi tạo."""
    from app.models.base import Base
    # Import tất cả models để SQLAlchemy nhận diện
    import app.models.user            # noqa: F401
    import app.models.quiz            # noqa: F401
    import app.models.card            # noqa: F401
    import app.models.user_card_stat  # noqa: F401
    import app.models.measure_word    # noqa: F401
    import app.models.grammar_point   # noqa: F401
    import app.models.sentence        # noqa: F401
    Base.metadata.create_all(bind=engine)
