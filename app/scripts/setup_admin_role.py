"""
Script cập nhật vai trò quản trị viên trong database:
- Đặt cờ is_admin = True cho tài khoản cnv1902@gmail.com
- Đặt is_admin = False cho các tài khoản còn lại
"""
import sys
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app.database import SessionLocal
from app.models.user import User
from app.models.quiz import Quiz
from app.models.card import Card
from app.models.user_card_stat import UserCardStat

def setup_admin():
    db = SessionLocal()
    target_email = "cnv1902@gmail.com"
    try:
        # 1. Tìm hoặc tạo user với email cnv1902@gmail.com
        user = db.query(User).filter(User.email == target_email).first()
        if user:
            user.is_admin = True
            print(f"[OK] Đã cập nhật is_admin=True cho tài khoản hiện có: {user.username} ({user.email})")
        else:
            # Tạo tài khoản cnv1902@gmail.com với quyền Admin
            from app.services.auth_service import hash_password
            new_admin = User(
                username="cnv1902",
                email=target_email,
                full_name="Quản Trị Viên",
                hashed_password=hash_password("admin123456"),
                is_admin=True,
                is_active=True,
                cards_per_round=10,
            )
            db.add(new_admin)
            print(f"[OK] Đã tạo mới tài khoản Admin: cnv1902 ({target_email})")

        # 2. Đặt is_admin = False cho tất cả các user khác
        other_users = db.query(User).filter(User.email != target_email).all()
        for u in other_users:
            if u.is_admin:
                u.is_admin = False
                print(f"[INFO] Đã hạ quyền tài khoản {u.username} ({u.email}) về User thường.")

        db.commit()
        print("[SUCCESS] Hoàn tất cấu hình phân quyền Admin!")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Lỗi khi cấu hình: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    setup_admin()
