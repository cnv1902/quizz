/**
 * cards.js — Alias trỏ sang CardApi trong quizApi.js
 */
if (typeof CardApi === "undefined") {
  window.CardApi = {
    getAll: () => Api.get('/cards'),
    getById: (id) => Api.get(`/cards/${id}`),
    adminCreate: (data) => Api.post('/cards/admin', data),
    adminUpdate: (id, data) => Api.put(`/cards/admin/${id}`, data),
    adminDelete: (id) => Api.delete(`/cards/admin/${id}`),
    adminBulkCreate: (items) => Api.post('/cards/admin/bulk', { items }),
    adminBulkDelete: (ids) => Api.post('/cards/admin/bulk-delete', { ids }),
  };
}
