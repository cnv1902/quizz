from datetime import datetime, timedelta
from typing import Optional
import httpx
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.crud import crud_user
from app.models.user import User

import bcrypt

# Bcrypt context cho hash password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# === Password Utilities ===

def hash_password(password: str) -> str:
    """Hash mật khẩu bằng bcrypt an toàn."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu đầu vào khớp với hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8"))
    except Exception:
        return pwd_context.verify(plain_password, hashed_password)


# === JWT Utilities ===

def create_access_token(user_id: int, username: str, is_admin: bool) -> str:
    """
    Tạo JWT access token.
    Payload gồm: sub (user_id), username, is_admin, exp.
    """
    expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "username": username,
        "is_admin": is_admin,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Giải mã JWT token. Trả về payload dict hoặc None nếu không hợp lệ.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


# === Auth Business Logic ===

def register_user(
    db: Session, username: str, email: str, full_name: str, password: str
) -> User:
    """
    Đăng ký tài khoản mới.
    Raises ValueError nếu username hoặc email đã tồn tại.
    """
    # Kiểm tra username đã tồn tại
    if crud_user.get_by_username(db, username):
        raise ValueError("Username đã được sử dụng")
    # Kiểm tra email đã tồn tại
    if crud_user.get_by_email(db, email):
        raise ValueError("Email đã được sử dụng")

    hashed = hash_password(password)

    return crud_user.create(
        db=db,
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=hashed,
        is_admin=False,
    )



def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Xác thực user bằng username/password.
    Trả về User nếu đúng, None nếu sai.
    """
    user = crud_user.get_by_username(db, username)
    if not user:
        return None
    if not user.hashed_password:
        return None  # User đăng nhập bằng Google, không có password
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


# === Google OAuth2 ===

def get_google_auth_url(state: str = "") -> str:
    """Tạo URL redirect tới Google OAuth2 consent screen."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{settings.GOOGLE_AUTH_URL}?{query}"


async def exchange_google_code(code: str) -> Optional[dict]:
    """
    Đổi authorization code lấy access_token từ Google.
    Trả về user info dict hoặc None nếu thất bại.
    """
    async with httpx.AsyncClient() as client:
        # Đổi code lấy tokens
        token_resp = await client.post(
            settings.GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            return None
        tokens = token_resp.json()
        access_token = tokens.get("access_token")
        if not access_token:
            return None

        # Lấy thông tin user từ Google
        user_resp = await client.get(
            settings.GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            return None
        return user_resp.json()


async def login_or_register_google(db: Session, google_user_info: dict) -> tuple[User, bool]:
    """
    Đăng nhập hoặc tạo tài khoản mới bằng Google.
    Trả về (User, is_new_user).
    """
    google_id = google_user_info.get("sub")
    email = google_user_info.get("email", "").lower()
    name = google_user_info.get("name", "Google User")

    # Tìm user theo google_id trước
    user = crud_user.get_by_google_id(db, google_id)
    if user:
        return user, False

    # Tìm user theo email (trường hợp đã đăng ký thường nhưng dùng cùng email)
    user = crud_user.get_by_email(db, email)
    if user:
        # Liên kết Google ID vào tài khoản hiện tại
        crud_user.update(db, user, google_id=google_id)
        return user, False

    # Tạo tài khoản mới từ Google
    username = email.split("@")[0].lower().replace(".", "_")
    # Đảm bảo username unique
    base_username = username
    counter = 1
    while crud_user.get_by_username(db, username):
        username = f"{base_username}_{counter}"
        counter += 1

    new_user = crud_user.create(
        db=db,
        username=username,
        email=email,
        full_name=name,
        google_id=google_id,
        is_admin=False,
    )
    return new_user, True

