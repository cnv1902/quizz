from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserSettingsUpdate
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Đăng ký tài khoản mới.
    Người dùng đầu tiên đăng ký sẽ được cấp quyền admin.
    """
    try:
        user = auth_service.register_user(
            db=db,
            username=user_data.username,
            email=str(user_data.email),
            full_name=user_data.full_name,
            password=user_data.password,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    token = auth_service.create_access_token(user.id, user.username, user.is_admin)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        is_admin=user.is_admin,
    )


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Đăng nhập bằng username/password, nhận JWT token."""
    user = auth_service.authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username hoặc mật khẩu không đúng",
        )
    token = auth_service.create_access_token(user.id, user.username, user.is_admin)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        is_admin=user.is_admin,
    )


@router.get("/google")
def google_login():
    """Redirect tới Google OAuth2 consent screen."""
    url = auth_service.get_google_auth_url()
    return RedirectResponse(url=url)


@router.get("/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Google OAuth2 callback.
    Đổi code lấy user info → tạo hoặc đăng nhập tài khoản → trả JWT.
    """
    google_user_info = await auth_service.exchange_google_code(code)
    if not google_user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xác thực với Google",
        )

    user, is_new = await auth_service.login_or_register_google(db, google_user_info)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa",
        )

    token = auth_service.create_access_token(user.id, user.username, user.is_admin)

    # Redirect về frontend với token trong fragment
    frontend_url = f"/pages/login.html#/auth/callback?token={token}&is_new={str(is_new).lower()}"
    return RedirectResponse(url=frontend_url)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Lấy thông tin user đang đăng nhập."""
    return current_user


@router.put("/me/settings", response_model=UserResponse)
def update_settings(
    settings_data: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cập nhật cài đặt cá nhân (cards_per_round, full_name)."""
    from app.crud import crud_user
    updates = settings_data.model_dump(exclude_none=True)
    if updates:
        crud_user.update(db, current_user, **updates)
    return current_user
