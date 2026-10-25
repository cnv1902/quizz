/**
 * quizzes.js — Alias trỏ sang QuizApi trong quizApi.js
 */
if (typeof QuizApi === "undefined") {
  window.QuizApi = {
    getAll: () => Api.get('/quizzes'),
    getById: (id) => Api.get(`/quizzes/${id}`),
    getCards: (quizId) => Api.get(`/quizzes/${quizId}/cards`),
    getCardsPriority: (quizId) => Api.get(`/quizzes/${quizId}/cards/priority`),
    adminGetAll: () => Api.get('/quizzes/admin/all'),
    adminCreate: (data) => Api.post('/quizzes/admin', data),
    adminUpdate: (id, data) => Api.put(`/quizzes/admin/${id}`, data),
    adminDelete: (id) => Api.delete(`/quizzes/admin/${id}`),
    adminImportExcel: (quizId, formData) => Api.postForm(`/quizzes/admin/${quizId}/import`, formData),
    downloadTemplate: () => { window.location.href = '/api/v1/quizzes/admin/template'; },
  };
}
