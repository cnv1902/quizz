/**
 * api.js — Lớp API: wrapper cho fetch() với JWT auth tự động.
 * Mọi lời gọi API đều đi qua đây, KHÔNG nhúng fetch() trực tiếp vào UI code.
 */

const API_BASE = '/api/v1';

/** Lấy JWT token từ localStorage. */
function getToken() {
  return localStorage.getItem('hanziquizz_token');
}

/** Lưu JWT token vào localStorage. */
function setToken(token) {
  localStorage.setItem('hanziquizz_token', token);
}

/** Xóa JWT token (logout). */
function clearToken() {
  localStorage.removeItem('hanziquizz_token');
  localStorage.removeItem('hanziquizz_user');
}

/**
 * Hàm fetch wrapper cơ bản.
 * Tự động inject Authorization header nếu có token.
 * @param {string} path - API path (không có /api/v1)
 * @param {object} options - fetch options
 * @returns {Promise<any>} - JSON response
 */
async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  // 401 → tự động logout
  if (response.status === 401) {
    clearToken();
    window.dispatchEvent(new CustomEvent('auth:logout'));
    throw new Error('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message = data?.detail || `Lỗi ${response.status}`;
    throw new Error(message);
  }

  return data;
}

/**
 * GET request.
 * @param {string} path
 * @param {object} params - query params object
 */
async function apiGet(path, params = {}) {
  const query = Object.keys(params).length
    ? '?' + new URLSearchParams(params).toString()
    : '';
  return apiFetch(`${path}${query}`, { method: 'GET' });
}

/**
 * POST request với JSON body.
 * @param {string} path
 * @param {object} body
 */
async function apiPost(path, body = {}) {
  return apiFetch(path, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * PUT request với JSON body.
 * @param {string} path
 * @param {object} body
 */
async function apiPut(path, body = {}) {
  return apiFetch(path, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
}

/**
 * DELETE request.
 * @param {string} path
 */
async function apiDelete(path) {
  return apiFetch(path, { method: 'DELETE' });
}

/**
 * POST với FormData (dùng cho upload file Excel).
 * @param {string} path
 * @param {FormData} formData
 */
async function apiPostForm(path, formData) {
  const token = getToken();
  const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers,
    body: formData,
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(data?.detail || `Lỗi ${response.status}`);
  }
  return data;
}

/**
 * Tải file (Blob) từ API có kèm JWT auth header và kích hoạt lưu trên trình duyệt.
 * @param {string} path - Đường dẫn API (không chứa tiền tố /api/v1)
 * @param {string} defaultFilename - Tên file lưu nếu response header không chỉ định
 */
async function apiDownload(path, defaultFilename = 'export.xlsx') {
  const token = getToken();
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'GET',
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || `Lỗi tải file (${response.status})`);
  }

  let filename = defaultFilename;
  const disposition = response.headers.get('Content-Disposition');
  if (disposition && disposition.includes('filename=')) {
    const match = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
    if (match && match[1]) {
      filename = match[1].replace(/['"]/g, '').trim();
    }
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }, 300);
  return filename;
}

// Export (dùng trong các file API layer)
window.Api = {
  get: apiGet,
  post: apiPost,
  put: apiPut,
  delete: apiDelete,
  postForm: apiPostForm,
  download: apiDownload,
};
window.ApiUtils = { getToken, setToken, clearToken };
