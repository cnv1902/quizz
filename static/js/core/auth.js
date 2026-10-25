/**
 * auth.js — Quản lý trạng thái xác thực người dùng.
 * Lưu/lấy thông tin user từ localStorage, kiểm tra đăng nhập.
 */

const AUTH_TOKEN_KEY = "hanziquizz_token";
const AUTH_USER_KEY = "hanziquizz_user";

const Auth = {
  /**
   * Lấy JWT token từ localStorage.
   * @returns {string|null}
   */
  getToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
  },

  /**
   * Kiểm tra user đã đăng nhập chưa.
   * @returns {boolean}
   */
  isLoggedIn() {
    return !!this.getToken();
  },

  /**
   * Lấy thông tin user hiện tại từ localStorage.
   * @returns {object|null}
   */
  getUser() {
    const raw = localStorage.getItem(AUTH_USER_KEY);
    try {
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },

  /**
   * Lưu token và thông tin user sau khi đăng nhập thành công.
   * @param {string} token - JWT access token
   * @param {object} user  - thông tin user {id, username, full_name, is_admin}
   */
  setSession(token, user) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
    window.dispatchEvent(new CustomEvent("auth:login", { detail: user }));
  },

  /**
   * Xóa session (logout).
   */
  clearSession() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    window.dispatchEvent(new CustomEvent("auth:logout"));
  },

  /**
   * Cập nhật thông tin user trong localStorage.
   */
  updateUser(partial) {
    const cur = this.getUser() || {};
    const merged = { ...cur, ...partial };
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(merged));
    return merged;
  },

  /**
   * Lấy số thẻ mỗi màn chơi (từ user hoặc localStorage hoặc mặc định 10).
   * Giá trị trả về có thể là số nguyên (>= 10) hoặc 'all' (tất cả thẻ).
   */
  getCardsPerRound() {
    const user = this.getUser();
    if (user && user.cards_per_round !== undefined && user.cards_per_round !== null) {
      if (user.cards_per_round === 0) return "all";
      return Math.max(10, parseInt(user.cards_per_round, 10) || 10);
    }
    const val = localStorage.getItem("cards_per_round");
    if (val === "all") return "all";
    return val ? Math.max(10, parseInt(val, 10) || 10) : 10;
  },

  /**
   * Lưu số thẻ mỗi màn chơi (từ 10 đến 'all').
   */
  async setCardsPerRound(val) {
    let toStore = val;
    let apiVal = 10;
    if (val === "all" || val === 0 || String(val).trim().toLowerCase() === "all") {
      toStore = "all";
      apiVal = 0; // 0 đại diện cho 'all'
    } else {
      toStore = Math.max(10, parseInt(val, 10) || 10);
      apiVal = toStore;
    }

    localStorage.setItem("cards_per_round", toStore);
    if (this.isLoggedIn() && window.Api?.put) {
      try {
        await window.Api.put("/auth/me/settings", { cards_per_round: apiVal });
        this.updateUser({ cards_per_round: apiVal });
      } catch (err) {
        console.warn("Failed to update user cards_per_round on server:", err);
      }
    }
    return toStore;
  },

  /**
   * Kiểm tra user có phải admin không.
   * @returns {boolean}
   */
  isAdmin() {
    const user = this.getUser();
    return user?.is_admin === true;
  },

  /**
   * Guard: redirect về login nếu chưa đăng nhập.
   * Gọi ở đầu mỗi page cần auth.
   */
  requireAuth() {
    if (!this.isLoggedIn()) {
      window.location.href = "/pages/login.html";
      return false;
    }
    return true;
  },

  /**
   * Guard: redirect về home nếu đã đăng nhập.
   * Gọi ở trang login/register.
   */
  requireGuest() {
    if (this.isLoggedIn()) {
      window.location.href = "/";
      return false;
    }
    return true;
  },

  /**
   * Guard: chỉ cho admin truy cập.
   */
  requireAdmin() {
    if (!this.isLoggedIn()) {
      window.location.href = "/pages/login.html";
      return false;
    }
    if (!this.isAdmin()) {
      window.location.href = "/pages/404.html";
      return false;
    }
    return true;
  },

  /**
   * Xử lý Google OAuth2 callback: đọc token từ URL fragment.
   * Gọi ở trang /auth/callback.
   */
  handleGoogleCallback() {
    const hash = window.location.hash.slice(1);
    const params = new URLSearchParams(hash.replace("/auth/callback?", ""));
    const token = params.get("token");
    if (!token) return false;

    // Lấy thông tin user từ API
    ApiUtils.setToken(token);
    return true;
  },
};

// Xử lý sự kiện logout toàn cục (từ api.js khi nhận 401)
window.addEventListener("auth:logout", () => {
  Auth.clearSession();
  const path = window.location.pathname;
  if (path.includes("/admin/")) {
    window.location.href = "/pages/login.html";
  }
});

window.Auth = Auth;
