/**
 * quizApi.js — API Layer cho Quizzes và Cards.
 * Mọi lời gọi liên quan đến quiz đều đi qua đây.
 */

const QuizApi = {
  /** Lấy danh sách tất cả quizzes. */
  getAll: () => Api.get('/quizzes'),

  /** Lấy chi tiết quiz theo ID. */
  getById: (id) => Api.get(`/quizzes/${id}`),

  /** Lấy thẻ của quiz theo thứ tự thông thường. */
  getCards: (quizId) => Api.get(`/quizzes/${quizId}/cards`),

  /** Lấy thẻ của quiz theo priority (Bổ Túc mode). */
  getCardsPriority: (quizId) => Api.get(`/quizzes/${quizId}/cards/priority`),

  // === Admin ===

  /** [Admin] Lấy tất cả quiz (kể cả inactive). */
  adminGetAll: () => Api.get('/quizzes/admin/all'),

  /** [Admin] Tạo quiz mới. */
  adminCreate: (data) => Api.post('/quizzes/admin', data),

  /** [Admin] Cập nhật quiz. */
  adminUpdate: (id, data) => Api.put(`/quizzes/admin/${id}`, data),

  /** [Admin] Xóa quiz. */
  adminDelete: (id) => Api.delete(`/quizzes/admin/${id}`),

  /** [Admin] Xuất danh sách tất cả bộ quizz ra file Excel. */
  adminExport: () => Api.download('/quizzes/admin/export', 'danh_sach_bo_quizz.xlsx'),

  /** [Admin] Xuất danh sách thẻ học của 1 quiz ra file Excel. */
  adminExportCards: (quizId) => Api.download(`/quizzes/admin/${quizId}/export`, `the_hoc_quizz_${quizId}.xlsx`),

  /** [Admin] Import từ Excel hoặc CSV. */
  adminImportExcel: (quizId, formData) => Api.postForm(`/quizzes/admin/${quizId}/import`, formData),

  /** [Admin] Tải file Excel mẫu (.xlsx). */
  downloadTemplate: () => {
    window.location.href = '/api/v1/quizzes/admin/template';
  },
};

const CardApi = {
  /** Lấy tất cả thẻ hệ thống (chế độ Tất cả thẻ). */
  getAll: (priority = false) => Api.get(`/cards/all${priority ? '?priority=true' : ''}`),

  /** [Admin] Tạo thẻ mới. */
  adminCreate: (data) => Api.post('/cards/admin', data),

  /** [Admin] Nhập hàng loạt thẻ vào quiz. */
  adminBulkCreate: (quizId, cards) => Api.post('/cards/admin/bulk', { quiz_id: quizId, cards }),

  /** [Admin] Cập nhật thẻ. */
  adminUpdate: (id, data) => Api.put(`/cards/admin/${id}`, data),

  /** [Admin] Xóa thẻ. */
  adminDelete: (id) => Api.delete(`/cards/admin/${id}`),

  /** [Admin] Xóa hàng loạt thẻ. */
  adminBulkDelete: (cardIds) => Api.post('/cards/admin/bulk-delete', { card_ids: cardIds }),
};


const ProgressApi = {
  /** Sync batch kết quả game. */
  syncBatch: (results, gameType, quizId = null) =>
    Api.post('/progress/batch', { results, game_type: gameType, quiz_id: quizId }),

  /** Lấy thống kê tiến độ theo quiz. */
  getStats: (quizId) => Api.get(`/progress/stats/${quizId}`),

  /** Lấy tổng quan tiến độ người dùng (streak, mastered, review_needed). */
  getSummary: () => Api.get('/progress/summary'),
};

const UserApi = {
  /** Lấy thông tin user hiện tại. */
  getMe: () => Api.get('/auth/me'),

  /** Cập nhật cài đặt cá nhân. */
  updateSettings: (data) => Api.put('/auth/me/settings', data),

  /** [Admin] Danh sách users. */
  adminGetAll: () => Api.get('/users/admin'),

  /** [Admin] Cập nhật user. */
  adminUpdate: (id, data) => Api.put(`/users/admin/${id}`, data),

  /** [Admin] Xóa user. */
  adminDelete: (id) => Api.delete(`/users/admin/${id}`),

  /** [Admin] Xuất danh sách người dùng ra file Excel. */
  adminExport: () => Api.download('/users/admin/export', 'danh_sach_nguoi_dung.xlsx'),
};

const SentenceSetApi = {
  /** Lấy danh sách các bộ câu đang active kèm số lượng câu. */
  getAll: () => Api.get('/sentence-sets'),

  /** Lấy chi tiết bộ câu. */
  getById: (id) => Api.get(`/sentence-sets/${id}`),

  /** Lấy tất cả câu trong bộ câu. */
  getSentences: (id) => Api.get(`/sentence-sets/${id}/sentences`),

  // === Admin ===
  /** [Admin] Danh sách tất cả bộ câu. */
  adminGetAll: () => Api.get('/sentence-sets/admin/all'),

  /** [Admin] Xuất danh sách tất cả bộ câu ra file Excel. */
  adminExport: () => Api.download('/sentence-sets/admin/export', 'danh_sach_bo_cau.xlsx'),

  /** [Admin] Xuất danh sách câu trong một bộ câu ra file Excel. */
  adminExportSentences: (setId) => Api.download(`/sentence-sets/admin/${setId}/export`, `cau_ghep_bo_${setId}.xlsx`),

  /** [Admin] Tạo bộ câu mới. */
  adminCreate: (data) => Api.post('/sentence-sets/admin', data),

  /** [Admin] Cập nhật bộ câu. */
  adminUpdate: (id, data) => Api.put(`/sentence-sets/admin/${id}`, data),

  /** [Admin] Xóa bộ câu. */
  adminDelete: (id) => Api.delete(`/sentence-sets/admin/${id}`),

  /** [Admin] Import Excel trực tiếp vào bộ câu. */
  adminImportExcel: (setId, formData) => Api.postForm(`/sentence-sets/admin/${setId}/import`, formData),
};

const MeasureWordApi = {
  /** [Admin] Xuất danh mục lượng từ ra file Excel. */
  adminExport: () => Api.download('/measure-words/admin/export', 'danh_sach_luong_tu.xlsx'),
};

const GrammarApi = {
  /** [Admin] Xuất danh mục ngữ pháp ra file Excel. */
  adminExport: () => Api.download('/grammar/admin/export', 'danh_sach_ngu_phap.xlsx'),
};

window.QuizApi        = QuizApi;
window.CardApi        = CardApi;
window.SentenceSetApi = SentenceSetApi;
window.MeasureWordApi = MeasureWordApi;
window.GrammarApi     = GrammarApi;
window.ProgressApi    = ProgressApi;
window.UserApi        = UserApi;
