/**
 * navbar.js — Quản lý hiển thị thanh điều hướng và menu trượt (mobile drawer)
 * Tự động đồng bộ trạng thái đăng nhập, active link và cấu hình trên mọi trang.
 */

(function () {
  function initNavbar() {
    const navbar = document.querySelector(".navbar");
    if (!navbar) return;

    // 1. Kiểm tra / Tạo nút Hamburger trên Navbar
    let hamburgerBtn = navbar.querySelector(".nav-hamburger-btn");
    if (!hamburgerBtn) {
      hamburgerBtn = document.createElement("button");
      hamburgerBtn.type = "button";
      hamburgerBtn.className = "nav-hamburger-btn";
      hamburgerBtn.setAttribute("aria-label", "Mở menu");
      hamburgerBtn.innerHTML = `
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      `;
      navbar.appendChild(hamburgerBtn);
    }

    // 2. Kiểm tra / Tạo Backdrop & Mobile Drawer trong body
    let backdrop = document.querySelector(".mobile-nav-backdrop");
    if (!backdrop) {
      backdrop = document.createElement("div");
      backdrop.className = "mobile-nav-backdrop";
      document.body.appendChild(backdrop);
    }

    let drawer = document.querySelector(".mobile-nav-drawer");
    if (!drawer) {
      drawer = document.createElement("aside");
      drawer.className = "mobile-nav-drawer";
      drawer.setAttribute("aria-label", "Menu điều hướng trên di động");
      document.body.appendChild(drawer);
    }

    // Lấy thông tin user hiện tại
    const isAuth = window.Auth?.isLoggedIn?.() || false;
    const user = window.Auth?.getUser?.() || null;
    const isAdmin = window.Auth?.isAdmin?.() || false;
    const currentPath = window.location.pathname.toLowerCase();

    const isHome = currentPath === "/" || currentPath.endsWith("/index.html") || currentPath === "";
    const isMeasureWords = currentPath.includes("measure-words");
    const isGrammar = currentPath.includes("grammar");
    const isGameSetup = currentPath.includes("game-setup");

    const displayName = user?.full_name || user?.username || "Bạn";
    const avatarChar = (displayName.trim().charAt(0) || "U").toUpperCase();

    // 3. Render nội dung Drawer
    drawer.innerHTML = `
      <div class="mobile-drawer-header">
        <a href="/" class="mobile-drawer-brand">
          <img src="/static/img/HanziQuizz-Favicon.png" alt="HanziQuizz Logo" />
          <span>HanziQuizz</span>
        </a>
        <button type="button" class="mobile-drawer-close" id="mobileDrawerCloseBtn" aria-label="Đóng menu">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div class="mobile-drawer-user">
        <div class="mobile-drawer-avatar">
          ${isAuth ? avatarChar : "👤"}
        </div>
        <div class="mobile-drawer-user-info">
          <div class="mobile-drawer-name">${isAuth ? escapeHtml(displayName) : "Khách"}</div>
          <div class="mobile-drawer-sub">
            ${isAuth ? (isAdmin ? "👑 Quản trị viên" : "✨ Học viên") : "Chưa đăng nhập"}
          </div>
        </div>
      </div>

      <nav class="mobile-drawer-nav">
        <a href="/" class="mobile-drawer-link ${isHome ? 'active' : ''}">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
          </svg>
          <span>Học từ vựng</span>
        </a>

        <a href="/pages/measure-words.html" class="mobile-drawer-link ${isMeasureWords ? 'active' : ''}">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
          </svg>
          <span>Cẩm nang lượng từ</span>
        </a>

        <a href="/pages/grammar.html" class="mobile-drawer-link ${isGrammar ? 'active' : ''}">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="4 7 4 4 20 4 20 7"></polyline>
            <line x1="9" y1="20" x2="15" y2="20"></line>
            <line x1="12" y1="4" x2="12" y2="20"></line>
          </svg>
          <span>Cẩm nang ngữ pháp</span>
        </a>

        <div class="mobile-drawer-divider"></div>

        <button type="button" class="mobile-drawer-link" id="mobileDrawerConfigBtn" style="background:none; border:none; width:100%; text-align:left; cursor:pointer;">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
          <span>Cấu hình số câu / thẻ</span>
        </button>

        <button type="button" class="mobile-drawer-link" id="mobileDrawerPwaBtn" style="background:none; border:none; width:100%; text-align:left; cursor:pointer; color: var(--accent);">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect>
            <line x1="12" y1="18" x2="12.01" y2="18"></line>
          </svg>
          <span style="font-weight:700;">📲 Cài đặt ứng dụng</span>
        </button>

        ${
          isAdmin
            ? `
          <a href="/pages/admin/quizzes.html" class="mobile-drawer-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="7" height="7"></rect>
              <rect x="14" y="3" width="7" height="7"></rect>
              <rect x="14" y="14" width="7" height="7"></rect>
              <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
            <span>Trang quản trị (Admin)</span>
          </a>
        `
            : ""
        }
      </nav>

      <div class="mobile-drawer-footer">
        ${
          isAuth
            ? `
          <button type="button" class="btn btn-secondary btn-full" id="mobileDrawerLogoutBtn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            Đăng xuất
          </button>
        `
            : `
          <div style="display:flex; flex-direction:column; gap:8px;">
            <a href="/pages/login.html" class="btn btn-secondary btn-full">Đăng nhập</a>
            <a href="/pages/register.html" class="btn btn-primary btn-full">Đăng ký tài khoản</a>
          </div>
        `
        }
      </div>
    `;

    // 4. Các hàm mở/đóng Drawer
    function openDrawer() {
      drawer.classList.add("is-open");
      backdrop.classList.add("is-open");
      document.body.style.overflow = "hidden"; // Ngăn cuộn nền
    }

    function closeDrawer() {
      drawer.classList.remove("is-open");
      backdrop.classList.remove("is-open");
      document.body.style.overflow = "";
    }

    hamburgerBtn.addEventListener("click", openDrawer);
    backdrop.addEventListener("click", closeDrawer);
    document.getElementById("mobileDrawerCloseBtn")?.addEventListener("click", closeDrawer);

    // Bấm ESC để đóng
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && drawer.classList.contains("is-open")) {
        closeDrawer();
      }
    });

    // Nút Cấu hình trong Drawer
    document.getElementById("mobileDrawerConfigBtn")?.addEventListener("click", () => {
      closeDrawer();
      // Nếu trang hiện tại có modal cấu hình, mở nó
      const pageBtnConfig = document.getElementById("btnOpenConfig") || document.getElementById("btnNavConfig") || document.getElementById("btnOpenConfigInline");
      if (pageBtnConfig) {
        pageBtnConfig.click();
      } else {
        window.location.href = "/pages/game-setup.html?mode=all";
      }
    });

    // Nút Cài đặt ứng dụng PWA trong Drawer
    const drawerPwaBtn = document.getElementById("mobileDrawerPwaBtn");
    if (drawerPwaBtn && window.setupPwaInstallButton) {
      window.setupPwaInstallButton(drawerPwaBtn);
    }

    // Nút Đăng xuất trong Drawer
    document.getElementById("mobileDrawerLogoutBtn")?.addEventListener("click", () => {
      window.Auth?.clearSession?.();
      window.location.reload();
    });
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Tự động chạy khi DOM sẵn sàng
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initNavbar);
  } else {
    initNavbar();
  }
})();
