from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.auth_service import decode_access_token
from app.crud import crud_user
from app.models.user import User

# Bearer token security scheme
security = HTTPBearer(auto_error=False)


def get_db() -> Generator:
    """Dependency: cung cấp DB session cho mỗi request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Dependency: lấy user hiện tại từ JWT token.
    Trả về None nếu không có token (cho các endpoint public).
    """
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    if not user_id:
        return None
    return crud_user.get_by_id(db, user_id)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency: bắt buộc phải đăng nhập.
    Raise 401 nếu không có token hoặc token không hợp lệ.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Vui lòng đăng nhập để tiếp tục",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = int(payload.get("sub", 0))
    user = crud_user.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa",
        )
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency: bắt buộc phải là admin.
    Raise 403 nếu không phải admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này",
        )
    return current_user
