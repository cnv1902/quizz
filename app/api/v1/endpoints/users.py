from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db, get_current_admin, get_current_user
from app.models.user import User
from app.schemas.user import UserListResponse, UserUpdate
from app.crud import crud_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/admin", response_model=List[UserListResponse])
def admin_list_users(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Danh sách tất cả người dùng."""
    return crud_user.get_all(db)


@router.put("/admin/{user_id}", response_model=UserListResponse)
def admin_update_user(
    user_id: int,
    user_data: UserUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Cập nhật thông tin user (trạng thái, role, cấu hình)."""
    user = crud_user.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")
    updates = user_data.model_dump(exclude_none=True)
    return crud_user.update(db, user, **updates)


@router.delete("/admin/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """[Admin] Xóa người dùng."""
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa tài khoản của chính mình",
        )
    user = crud_user.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")
    crud_user.delete(db, user)
