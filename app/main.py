from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import time

from app.config import settings
from app.database import create_tables
from app.dependencies import get_db
from app.api.v1.router import api_router

# Tạo FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Nền tảng học tiếng Trung qua trò chơi tương tác",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

# Server reload timestamp
SERVER_BOOT_TIME = int(time.time())

# Static & Pages directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
PAGES_DIR = os.path.join(BASE_DIR, "pages")

# Mount static files (cho phép trình duyệt cache bình thường dựa trên query param ?v=)
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Jinja2 Templates engine cho các trang HTML
templates = Jinja2Templates(directory=PAGES_DIR)
templates.env.globals["v"] = SERVER_BOOT_TIME


def render_template(request: Request, rel_path: str):
    """Render HTML template qua Jinja2 với biến version v tự động."""
    norm_path = rel_path.replace("\\", "/").strip("/")
    return templates.TemplateResponse(request, norm_path, {"v": SERVER_BOOT_TIME})


# Google OAuth2 root callback handler (khớp với Google Console http://localhost:8000/callback)
@app.get("/callback")
async def root_google_callback(code: str, db: Session = Depends(get_db)):
    from app.api.v1.endpoints.auth import google_callback
    return await google_callback(code=code, db=db)


@app.get("/robots.txt", response_class=PlainTextResponse)
def serve_robots_txt():
    """Cho phép tất cả bot/crawler (Googlebot, ClaudeBot, v.v.) thu thập dữ liệu."""
    return "User-agent: *\nAllow: /\n"


@app.get("/manifest.json")
def serve_manifest():
    """Phục vụ file PWA Web App Manifest."""
    manifest_path = os.path.join(STATIC_DIR, "manifest.json")
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/manifest+json")
    raise HTTPException(status_code=404, detail="Manifest not found")


@app.get("/sw.js")
def serve_service_worker():
    """Phục vụ file Service Worker tại root scope để quản lý toàn bộ website."""
    sw_path = os.path.join(STATIC_DIR, "sw.js")
    if os.path.exists(sw_path):
        return FileResponse(sw_path, media_type="application/javascript", headers={"Service-Worker-Allowed": "/"})
    raise HTTPException(status_code=404, detail="Service worker not found")


# Serve frontend HTML pages
@app.get("/")
async def serve_index(request: Request):
    index_path = os.path.join(PAGES_DIR, "index.html")
    if os.path.exists(index_path):
        return render_template(request, "index.html")
    return {"message": "HanziQuizz API is running", "docs": "/api/docs"}


@app.get("/pages/{page_path:path}")
async def serve_pages_html(request: Request, page_path: str):
    """Phục vụ trực tiếp các file HTML trong thư mục pages/ qua Jinja2."""
    asset_exts = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.json', '.map', '.woff', '.woff2', '.ttf')
    if any(page_path.lower().endswith(ext) for ext in asset_exts):
        raise HTTPException(status_code=404, detail="Asset not found")

    rel = page_path
    if not rel.endswith(".html"):
        rel += ".html"

    full = os.path.join(PAGES_DIR, rel)
    if os.path.isfile(full):
        return render_template(request, rel)

    return templates.TemplateResponse(request, "404.html", {"v": SERVER_BOOT_TIME}, status_code=404)


@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    """SPA fallback: phục vụ các file HTML trong thư mục pages/ qua Jinja2."""
    asset_exts = ('.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.json', '.map', '.woff', '.woff2', '.ttf')
    if any(full_path.lower().endswith(ext) for ext in asset_exts):
        raise HTTPException(status_code=404, detail="Asset not found")

    rel_path = full_path
    if rel_path.startswith("pages/"):
        rel_path = rel_path[6:]
    elif rel_path in ("pages", "", "index"):
        rel_path = "index.html"

    candidates = [
        rel_path,
        f"{rel_path}.html",
    ]
    for c in candidates:
        full = os.path.join(PAGES_DIR, c)
        if os.path.isfile(full) and full.endswith(".html"):
            return render_template(request, c)

    # Nếu truy cập URL không tồn tại -> chuyển đến trang 404.html
    return templates.TemplateResponse(request, "404.html", {"v": SERVER_BOOT_TIME}, status_code=404)


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return templates.TemplateResponse(request, "404.html", {"v": SERVER_BOOT_TIME}, status_code=404)
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=404, content={"detail": exc.detail or "Not Found"})


@app.exception_handler(403)
async def custom_403_handler(request: Request, exc: HTTPException):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return templates.TemplateResponse(request, "404.html", {"v": SERVER_BOOT_TIME}, status_code=403)
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=403, content={"detail": exc.detail or "Forbidden"})


@app.on_event("startup")
async def startup_event():
    """Khởi tạo database và chạy voice sync ngầm khi server start."""
    create_tables()
    print(f"[OK] {settings.APP_NAME} v{settings.APP_VERSION} started!")
    print(f"[Docs] API Docs: http://localhost:8000/api/docs")

    # Chạy voice sync ngầm sau 5 giây — không block server startup
    import threading
    import time
    from app.services import voice_service

    def deferred_voice_sync():
        time.sleep(5)
        print("[VoiceSync] Bắt đầu kiểm tra và sinh voice cho các mục còn thiếu...")
        try:
            counts = voice_service.sync_all_missing_voices()
            total = sum(counts.values())
            if total > 0:
                print(f"[VoiceSync] Đã sinh {total} file audio mới: {counts}")
            else:
                print("[VoiceSync] Tất cả audio đã đầy đủ.")
        except Exception as e:
            print(f"[VoiceSync] Lỗi khi sync voice: {e}")

    threading.Thread(target=deferred_voice_sync, daemon=True).start()
