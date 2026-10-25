// HanziQuizz Service Worker v1.0
const CACHE_NAME = "hanziquizz-cache-v1";

// Các tài nguyên tĩnh cốt lõi cần nạp vào bộ nhớ đệm
const CORE_ASSETS = [
  "/",
  "/manifest.json",
  "/static/css/game/theme.css",
  "/static/css/game/flashcard.css",
  "/static/css/game/pikachu.css",
  "/static/css/game/multiple_choice.css",
  "/static/js/core/api.js",
  "/static/js/core/auth.js",
  "/static/js/components/navbar.js",
  "/static/js/components/toast.js",
  "/static/js/components/audioPlayer.js",
  "/static/js/api/quizApi.js",
  "/static/js/services/syncService.js",
  "/static/js/pwa.js",
  "/static/img/HanziQuizz-Favicon.png",
  "/static/img/icons/icon-192.png",
  "/static/img/icons/icon-512.png"
];

// Cài đặt Service Worker và cache core assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(CORE_ASSETS).catch((err) => {
        console.warn("[SW] Cache core assets partially failed:", err);
      });
    })
  );
  self.skipWaiting();
});

// Kích hoạt và dọn dẹp các cache phiên bản cũ
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Chiến lược xử lý Request (Network-First với HTML/API, Cache-First với Static Assets)
self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Bỏ qua các API mutation hoặc POST/PUT/DELETE
  if (req.method !== "GET") {
    return;
  }

  // Bỏ qua API calls
  if (url.pathname.startsWith("/api/")) {
    return;
  }

  // Với Static files (CSS, JS, Fonts, Images) -> Cache-First, fallback to Network
  if (
    url.pathname.startsWith("/static/") ||
    url.pathname.endsWith(".png") ||
    url.pathname.endsWith(".css") ||
    url.pathname.endsWith(".js") ||
    url.pathname.endsWith(".woff2")
  ) {
    event.respondWith(
      caches.match(req).then((cached) => {
        if (cached) return cached;
        return fetch(req).then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // Với HTML Navigation Pages -> Network-First, fallback to Cache, fallback to Offline /
  event.respondWith(
    fetch(req)
      .then((response) => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
        }
        return response;
      })
      .catch(() => {
        return caches.match(req).then((cached) => {
          if (cached) return cached;
          return caches.match("/");
        });
      })
  );
});
