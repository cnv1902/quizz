# 🀄 HanziQuizz

Nền tảng học tiếng Trung qua trò chơi tương tác — Lật thẻ, Ghép đôi Pikachu, Trắc nghiệm, Điền từ.

## 🚀 Cài đặt & Chạy (Sprint 1)

### Yêu cầu
- Python 3.11+
- pip

### Bước 1: Cài đặt dependencies
```powershell
cd d:\quizz
pip install -r requirements.txt
```

### Bước 2: Chạy server
```powershell
python run.py
```
hoặc
```powershell
uvicorn app.main:app --reload --port 8000
```

### Bước 3: Truy cập
- **Trang chủ:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs
- **Login:** http://localhost:8000/pages/login.html
- **Register:** http://localhost:8000/pages/register.html
- **Admin Quizzes:** http://localhost:8000/pages/admin/quizzes.html
- **Admin Users:** http://localhost:8000/pages/admin/users.html
- **Game Setup:** http://localhost:8000/pages/game-setup.html?mode=all
- **Flashcard Game:** http://localhost:8000/pages/games/flashcard.html?mode=all&cards=10&priority=false&round=1

> 💡 **Lưu ý:** Người dùng đầu tiên đăng ký sẽ tự động được cấp quyền **Admin**.

---

## 📁 Cấu trúc dự án

```
d:/quizz/
├── app/                     # FastAPI backend
│   ├── models/              # SQLAlchemy ORM (User, Quiz, Card, UserCardStat)
│   ├── schemas/             # Pydantic DTOs
│   ├── crud/                # Database operations
│   ├── services/            # Business logic
│   ├── api/v1/endpoints/    # REST API endpoints
│   ├── config.py            # Settings (JWT, Google OAuth2)
│   ├── database.py          # SQLite engine
│   ├── dependencies.py      # FastAPI dependencies (auth guards)
│   └── main.py              # App entrypoint
│
├── static/
│   ├── css/game/theme.css   # Game design system
│   └── js/
│       ├── core/            # api.js, auth.js
│       ├── api/             # quizApi.js (Repository Pattern)
│       ├── components/      # toast.js
│       └── services/        # syncService.js (Background sync)
│
├── pages/
│   ├── index.html           # Trang chủ (danh sách quiz)
│   ├── login.html           # Đăng nhập
│   ├── register.html        # Đăng ký
│   ├── game-setup.html      # Cấu hình số thẻ/màn
│   ├── games/               # Game pages (Sprint 3-4)
│   └── admin/               # Admin portal (Sprint 2)
│
├── requirements.txt
├── run.py
└── hanziquizz.db            # SQLite DB (tự tạo khi chạy lần đầu)
```

## 🔑 API Endpoints

### Auth
| Method | URL | Mô tả |
|--------|-----|-------|
| POST | `/api/v1/auth/register` | Đăng ký |
| POST | `/api/v1/auth/login` | Đăng nhập |
| GET | `/api/v1/auth/google` | Google OAuth2 |
| GET | `/api/v1/auth/callback` | Google callback |
| GET | `/api/v1/auth/me` | Thông tin user hiện tại |

### Quizzes (yêu cầu JWT)
| Method | URL | Mô tả |
|--------|-----|-------|
| GET | `/api/v1/quizzes` | Danh sách quiz |
| GET | `/api/v1/quizzes/{id}/cards` | Thẻ theo thứ tự |
| GET | `/api/v1/quizzes/{id}/cards/priority` | Thẻ theo priority (Bổ Túc) |
| GET | `/api/v1/cards/all` | Tất cả thẻ hệ thống |
| POST | `/api/v1/progress/batch` | Sync kết quả game |

### Admin (yêu cầu is_admin=True)
| Method | URL | Mô tả |
|--------|-----|-------|
| POST | `/api/v1/quizzes/admin` | Tạo quiz |
| PUT | `/api/v1/quizzes/admin/{id}` | Sửa quiz |
| DELETE | `/api/v1/quizzes/admin/{id}` | Xóa quiz |
| POST | `/api/v1/quizzes/admin/{id}/import` | Import Excel |
| POST | `/api/v1/cards/admin` | Tạo thẻ |
| PUT | `/api/v1/cards/admin/{id}` | Sửa thẻ |
| DELETE | `/api/v1/cards/admin/{id}` | Xóa thẻ |
| GET | `/api/v1/users/admin` | Danh sách users |

## 📊 Format Excel Import

File `.xlsx` với cấu trúc:

| Cột A (Tiếng Việt) | Cột B (Pinyin) | Cột C (Chữ Hán) |
|---|---|---|
| Xin chào | nǐ hǎo | 你好 |
| Cảm ơn | xièxie | 谢谢 |

> Dòng đầu tiên là header (bị bỏ qua tự động).

## 🗓 Roadmap

- ✅ **Sprint 1** — Backend (Models/CRUD/Services/API) + Auth + Home page + Register/Login
- 🔲 **Sprint 2** — Admin Portal (Quản lý Quiz/Card/User + Import Excel)
- 🔲 **Sprint 3** — Game Portal (Flashcard + Bổ Túc + Background Sync)
- 🔲 **Sprint 4** — Pikachu + Trắc nghiệm + Điền từ
- 🔲 **Sprint 5** — Polish + PWA + Mobile responsive
