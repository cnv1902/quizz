/**
 * toast.js — Hệ thống thông báo Toast toàn cục.
 * Dùng: Toast.show('Thành công!', 'success')
 */

(function () {
  // Tạo container nếu chưa có
  function getContainer() {
    let el = document.getElementById("toast-container");
    if (!el) {
      el = document.createElement("div");
      el.id = "toast-container";
      document.body.appendChild(el);
    }
    return el;
  }

  /**
   * Hiển thị toast notification.
   * @param {string} message - Nội dung thông báo
   * @param {'success'|'error'|'info'} type - Loại toast
   * @param {number} duration - Thời gian hiển thị (ms), mặc định 3000
   */
  function show(message, type = "info", duration = 3000) {
    const container = getContainer();
    const icons = { success: "✓ ", error: "✗", info: "ℹ" };

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${icons[type] || "ℹ"}</span><span>${message}</span>`;

    container.appendChild(toast);

    // Auto remove
    setTimeout(() => {
      toast.style.animation = "toastOut 300ms ease forwards";
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  window.Toast = { show };
})();
