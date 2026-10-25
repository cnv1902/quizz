/**
 * HanziQuizz PWA Helper
 * Quản lý đăng ký Service Worker và thông báo cài đặt ứng dụng (A2HS - Add to Home Screen)
 */
(function () {
  // 1. Đăng ký Service Worker
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker
        .register("/sw.js")
        .then((reg) => {
          console.log("[PWA] Service Worker registered with scope:", reg.scope);
        })
        .catch((err) => {
          console.warn("[PWA] Service Worker registration failed:", err);
        });
    });
  }

  // 2. Quản lý sự kiện Cài đặt Ứng dụng
  let deferredPrompt = null;
  const isIos = /iphone|ipad|ipod/.test(window.navigator.userAgent.toLowerCase());
  const isInStandaloneMode = window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;

  // Nếu đã chạy trong app standalone thì không hiển thị nút cài đặt nữa
  if (isInStandaloneMode) {
    return;
  }

  // Tạo UI Banner Cài Đặt (Floating Bottom Banner hoặc nút bấm)
  function createInstallBanner() {
    if (document.getElementById("pwaInstallBanner")) return;

    const banner = document.createElement("div");
    banner.id = "pwaInstallBanner";
    banner.innerHTML = `
      <div class="pwa-banner-inner">
        <div class="pwa-banner-icon">
          <img src="/static/img/icons/icon-96.png" alt="HanziQuizz Icon" width="40" height="40" />
        </div>
        <div class="pwa-banner-text">
          <div class="pwa-banner-title">Cài đặt HanziQuizz</div>
          <div class="pwa-banner-sub">Học tiếng Trung mọi lúc, mượt như ứng dụng gốc</div>
        </div>
        <div class="pwa-banner-actions">
          <button id="btnPwaInstall" class="pwa-btn-install">Cài đặt</button>
          <button id="btnPwaDismiss" class="pwa-btn-close" aria-label="Đóng">&times;</button>
        </div>
      </div>
    `;

    // Style cho banner
    const style = document.createElement("style");
    style.textContent = `
      #pwaInstallBanner {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%) translateY(120%);
        width: calc(100% - 32px);
        max-width: 460px;
        background: var(--surface, #ffffff);
        border: 1px solid var(--border-strong, #e5e0d8);
        border-radius: var(--r-lg, 12px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        z-index: 9999;
        transition: transform 300ms cubic-bezier(0.16, 1, 0.3, 1);
        padding: 10px 14px;
        box-sizing: border-box;
      }
      #pwaInstallBanner.show {
        transform: translateX(-50%) translateY(0);
      }
      .pwa-banner-inner {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .pwa-banner-icon img {
        border-radius: 8px;
        display: block;
      }
      .pwa-banner-text {
        flex: 1;
        min-width: 0;
      }
      .pwa-banner-title {
        font-weight: 700;
        font-size: 0.92rem;
        color: var(--text, #1c1a17);
      }
      .pwa-banner-sub {
        font-size: 0.72rem;
        color: var(--text-2, #6b665f);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .pwa-banner-actions {
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .pwa-btn-install {
        background: var(--accent, #b33939);
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 0.82rem;
        font-weight: 700;
        cursor: pointer;
        transition: background-color 150ms ease;
      }
      .pwa-btn-install:hover {
        opacity: 0.9;
      }
      .pwa-btn-close {
        background: transparent;
        border: none;
        font-size: 1.4rem;
        line-height: 1;
        color: var(--text-3, #999);
        cursor: pointer;
        padding: 0 4px;
      }
    `;
    document.head.appendChild(style);
    document.body.appendChild(banner);

    // Xử lý nút Cài đặt
    document.getElementById("btnPwaInstall").addEventListener("click", async () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log("[PWA] User response to install prompt:", outcome);
        deferredPrompt = null;
        banner.classList.remove("show");
      } else if (isIos) {
        alert("Để cài đặt trên iPhone:\n1. Bấm nút Chia sẻ (biểu tượng mũi tên hướng lên ⎋)\n2. Chọn 'Thêm vào Màn hình chính' (Add to Home Screen ➕)");
      }
    });

    // Xử lý nút Đóng
    document.getElementById("btnPwaDismiss").addEventListener("click", () => {
      banner.classList.remove("show");
      sessionStorage.setItem("pwa_dismissed", "true");
    });
  }

  // Bắt sự kiện trên Chrome / Android
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;

    if (!sessionStorage.getItem("pwa_dismissed")) {
      createInstallBanner();
      setTimeout(() => {
        const b = document.getElementById("pwaInstallBanner");
        if (b) b.classList.add("show");
      }, 2000);
    }
  });

  // Sự kiện sau khi cài đặt thành công
  window.addEventListener("appinstalled", () => {
    console.log("[PWA] HanziQuizz was installed successfully!");
    const b = document.getElementById("pwaInstallBanner");
    if (b) b.remove();
  });

  // Hỗ trợ nút cài đặt tích hợp trong mobile drawer nếu có
  window.setupPwaInstallButton = function (buttonElement) {
    if (!buttonElement) return;
    if (isInStandaloneMode) {
      buttonElement.style.display = "none";
      return;
    }
    buttonElement.addEventListener("click", () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
      } else if (isIos) {
        alert("Để cài đặt trên iPhone:\n1. Bấm nút Chia sẻ ở thanh dưới Safari (⎋)\n2. Chọn 'Thêm vào Màn hình chính' ➕");
      } else {
        alert("Ứng dụng đã sẵn sàng! Mở menu trình duyệt (dấu 3 chấm) và chọn 'Cài đặt ứng dụng' hoặc 'Thêm vào màn hình chính'.");
      }
    });
  };
})();
