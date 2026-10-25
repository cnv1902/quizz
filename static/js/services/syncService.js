/**
 * syncService.js — Background Sync Service.
 * Gửi kết quả đúng/sai sau mỗi game lên server.
 * Nếu offline, lưu vào IndexedDB queue và sync khi có kết nối lại.
 */

const SyncService = (function () {
  const DB_NAME   = 'hanziquizz_sync';
  const DB_STORE  = 'pending_syncs';
  const DB_VERSION = 1;

  let db = null;

  // === IndexedDB Setup ===

  async function openDB() {
    return new Promise((resolve, reject) => {
      if (db) { resolve(db); return; }
      const req = indexedDB.open(DB_NAME, DB_VERSION);
      req.onupgradeneeded = (e) => {
        const idb = e.target.result;
        if (!idb.objectStoreNames.contains(DB_STORE)) {
          idb.createObjectStore(DB_STORE, { keyPath: 'id', autoIncrement: true });
        }
      };
      req.onsuccess = (e) => { db = e.target.result; resolve(db); };
      req.onerror   = (e) => reject(e.target.error);
    });
  }

  async function savePending(payload) {
    const idb = await openDB();
    return new Promise((resolve, reject) => {
      const tx = idb.transaction(DB_STORE, 'readwrite');
      tx.objectStore(DB_STORE).add({ ...payload, queued_at: Date.now() });
      tx.oncomplete = resolve;
      tx.onerror    = (e) => reject(e.target.error);
    });
  }

  async function getPending() {
    const idb = await openDB();
    return new Promise((resolve, reject) => {
      const tx = idb.transaction(DB_STORE, 'readonly');
      const req = tx.objectStore(DB_STORE).getAll();
      req.onsuccess = (e) => resolve(e.target.result);
      req.onerror   = (e) => reject(e.target.error);
    });
  }

  async function deletePending(id) {
    const idb = await openDB();
    return new Promise((resolve, reject) => {
      const tx = idb.transaction(DB_STORE, 'readwrite');
      tx.objectStore(DB_STORE).delete(id);
      tx.oncomplete = resolve;
      tx.onerror    = (e) => reject(e.target.error);
    });
  }

  // === Core Sync Logic ===

  /**
   * Gửi batch kết quả lên server.
   * Ưu tiên sendBeacon (không block page unload), fallback sang fetch.
   * @param {object} payload - { results, game_type, quiz_id }
   */
  async function sendToServer(payload) {
    const token = window.ApiUtils?.getToken?.() || localStorage.getItem('hanziquizz_token');
    if (!token) return false;

    const url = '/api/v1/progress/batch';
    const body = JSON.stringify(payload);
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };

    // Thử sendBeacon trước (hoạt động khi trang đóng)
    if (navigator.sendBeacon) {
      const blob = new Blob([body], { type: 'application/json' });
      // sendBeacon không hỗ trợ custom headers → dùng fetch với keepalive
    }

    // Dùng fetch với keepalive: true
    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers,
        body,
        keepalive: true,
      });
      return resp.ok;
    } catch {
      return false;
    }
  }

  /**
   * Gửi kết quả game. Nếu offline thì lưu queue.
   * @param {Array} results - [{card_id, is_correct}, ...]
   * @param {string} gameType - 'flashcard' | 'pikachu' | 'multiple_choice' | 'fill_in'
   * @param {number|null} quizId
   */
  async function syncResults(results, gameType, quizId = null) {
    const token = window.ApiUtils?.getToken?.() || localStorage.getItem('hanziquizz_token');
    if (!token) {
      // Khách chưa đăng nhập: không gửi kết quả lên server và không queue
      return;
    }

    if (!results || results.length === 0) return;

    const payload = {
      results,
      game_type: gameType,
      quiz_id: quizId,
    };

    if (!navigator.onLine) {
      // Offline → lưu vào queue
      await savePending(payload);
      console.log(`[SyncService] Offline — đã queue ${results.length} kết quả`);
      return;
    }

    const success = await sendToServer(payload);
    if (!success) {
      // Gửi thất bại → lưu queue
      await savePending(payload);
      console.warn('[SyncService] Gửi thất bại — đã queue để retry');
    } else {
      console.log(`[SyncService] Synced ${results.length} kết quả thành công`);
    }
  }

  /**
   * Flush queue: gửi tất cả pending items khi online lại.
   */
  async function flushQueue() {
    const token = window.ApiUtils?.getToken?.() || localStorage.getItem('hanziquizz_token');
    if (!token || !navigator.onLine) return;
    const pending = await getPending();
    if (pending.length === 0) return;

    console.log(`[SyncService] Flushing ${pending.length} pending syncs...`);
    for (const item of pending) {
      const { id, ...payload } = item;
      const success = await sendToServer(payload);
      if (success) {
        await deletePending(id);
        console.log(`[SyncService] Flushed item ${id}`);
      }
    }
  }

  // === Event Listeners ===
  window.addEventListener('online', () => {
    console.log('[SyncService] Online — flushing queue...');
    flushQueue();
  });

  /**
   * Gửi kết quả game Ghép câu (sentences).
   * @param {Array} results - [{sentence_id, is_correct}, ...]
   * @param {number|null} setId
   */
  async function syncSentenceResults(results, setId = null) {
    const token = window.ApiUtils?.getToken?.() || localStorage.getItem('hanziquizz_token');
    if (!token || !results || results.length === 0) return;

    const payload = {
      results: results.map(r => ({
        sentence_id: r.sentence_id || r.id,
        is_correct: Boolean(r.is_correct),
      })),
      set_id: setId ? parseInt(setId, 10) : null,
    };

    try {
      await fetch('/api/v1/sentences/progress/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
        keepalive: true,
      });
      console.log(`[SyncService] Synced ${results.length} kết quả ghép câu thành công`);
    } catch (err) {
      console.warn('[SyncService] Gửi kết quả ghép câu thất bại:', err);
    }
  }

  return { syncResults, syncSentenceResults, flushQueue };
})();

window.SyncService = SyncService;
