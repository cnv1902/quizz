from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user import User


def get_by_id(db: Session, user_id: int) -> Optional[User]:
    """Lấy user theo ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_by_username(db: Session, username: str) -> Optional[User]:
    """Lấy user theo username."""
    return db.query(User).filter(User.username == username.lower()).first()


def get_by_email(db: Session, email: str) -> Optional[User]:
    """Lấy user theo email."""
    return db.query(User).filter(User.email == email.lower()).first()


def get_by_google_id(db: Session, google_id: str) -> Optional[User]:
    """Lấy user theo Google ID."""
    return db.query(User).filter(User.google_id == google_id).first()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Lấy danh sách tất cả users (admin)."""
    return db.query(User).offset(skip).limit(limit).all()


def create(
    db: Session,
    username: str,
    email: str,
    full_name: str,
    hashed_password: Optional[str] = None,
    google_id: Optional[str] = None,
    is_admin: bool = False,
) -> Optional[User]:
    """Tạo user mới. Tuân thủ Explicit Assignment pattern."""
    try:
        db_user = User(
            username=username.lower(),
            email=email.lower(),
            full_name=full_name,
            hashed_password=hashed_password,
            google_id=google_id,
            is_admin=is_admin,
            is_active=True,
            cards_per_round=10,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise e


def update(db: Session, user: User, **fields) -> Optional[User]:
    """Cập nhật các trường của user. Dùng Explicit Assignment."""
    try:
        for key, value in fields.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise e


def delete(db: Session, user: User) -> bool:
    """Xóa user."""
    try:
        db.delete(user)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e


def count_all(db: Session) -> int:
    """Đếm tổng số users."""
    return db.query(User).count()
