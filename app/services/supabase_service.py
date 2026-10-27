"""
supabase_service.py — Quản lý kết nối Supabase Client (Python SDK).
Dùng cho các tính năng bổ sung của Supabase như Supabase Storage (lưu trữ file âm thanh / hình ảnh) hoặc Auth.
"""

from typing import Optional
from supabase import create_client, Client
from app.config import settings

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """Trả về singleton Supabase Client nếu SUPABASE_URL và SUPABASE_KEY được cấu hình."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        try:
            _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            return _supabase_client
        except Exception as e:
            print(f"[SupabaseService] Khởi tạo Supabase Client thất bại: {e}")
            return None
    return None
