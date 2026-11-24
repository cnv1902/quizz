from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud import crud_user
from app.models.user import User
from app.services.excel_export_service import create_styled_excel


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Lấy danh sách tất cả người dùng (Admin)."""
    return crud_user.get_all(db, skip=skip, limit=limit)


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Lấy thông tin người dùng theo ID."""
    return crud_user.get_by_id(db, user_id)


def update_user(db: Session, user_id: int, **fields) -> Optional[User]:
    """Cập nhật thông tin người dùng."""
    user = crud_user.get_by_id(db, user_id)
    if not user:
        return None
    return crud_user.update(db, user, **fields)


def delete_user(db: Session, user_id: int) -> bool:
    """Xóa tài khoản người dùng."""
    user = crud_user.get_by_id(db, user_id)
    if not user:
        return False
    return crud_user.delete(db, user)


def export_users_excel(db: Session) -> bytes:
    """Xuất toàn bộ danh sách người dùng ra file Excel."""
    users = crud_user.get_all(db, skip=0, limit=10000)
    
    headers = [
        "ID",
        "Tên đăng nhập",
        "Họ và tên",
        "Email",
        "Vai trò",
        "Trạng thái",
        "Số thẻ/màn",
        "Ngày tham gia",
    ]
    
    col_alignments = [
        "center",  # ID
        "left",    # Username
        "left",    # Full name
        "left",    # Email
        "center",  # Role
        "center",  # Status
        "center",  # Cards per round
        "center",  # Created at
    ]
    
    data_rows = []
    for u in users:
        role_label = "Quản trị viên" if u.is_admin else "Học viên"
        status_label = "Hoạt động" if u.is_active else "Bị khóa"
        cards_per_round = "Tất cả" if getattr(u, "cards_per_round", 10) == 0 else str(getattr(u, "cards_per_round", 10))
        created_str = u.created_at.strftime("%d/%m/%Y %H:%M") if u.created_at else ""
        
        data_rows.append([
            u.id,
            u.username,
            u.full_name or "",
            u.email,
            role_label,
            status_label,
            cards_per_round,
            created_str,
        ])
        
    return create_styled_excel(
        sheet_title="Danh sách người dùng",
        headers=headers,
        data_rows=data_rows,
        col_alignments=col_alignments,
    )
