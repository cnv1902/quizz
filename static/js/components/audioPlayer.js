/**
 * HanziQuizz AudioPlayer Component
 * Phát âm thanh chuẩn tiếng Trung Phổ thông (普通话 - Pǔtōnghuà) từ file MP3 đã tạo sẵn trên backend.
 * Tự động fallback sang Web Speech API nếu file mp3 chưa có hoặc gặp lỗi mạng.
 */
(function (global) {
  'use strict';

  const AudioPlayer = {
    currentAudio: null,

    /**
     * Dừng toàn bộ âm thanh đang phát (cả MP3 lẫn Web Speech).
     */
    stop: function () {
      if (this.currentAudio) {
        try {
          this.currentAudio.pause();
          this.currentAudio.currentTime = 0;
        } catch (_) {}
        this.currentAudio = null;
      }
      if ('speechSynthesis' in window) {
        try {
          window.speechSynthesis.cancel();
        } catch (_) {}
      }
      document.querySelectorAll('.is-audio-playing').forEach(function (el) {
        el.classList.remove('is-audio-playing');
      });
    },

    /**
     * Fallback sang Web Speech API của trình duyệt.
     */
    speechFallback: function (text, options) {
      options = options || {};
      if (!('speechSynthesis' in window) || !text) return;

      var btn = options.btnElement || null;
      try {
        window.speechSynthesis.cancel();
        var utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = options.lang || 'zh-CN';
        utterance.rate = options.rate || 0.85;

        if (btn) {
          btn.classList.add('is-audio-playing');
          utterance.onend = function () {
            btn.classList.remove('is-audio-playing');
          };
          utterance.onerror = function () {
            btn.classList.remove('is-audio-playing');
          };
        }
        window.speechSynthesis.speak(utterance);
      } catch (e) {
        console.warn('SpeechSynthesis error:', e);
        if (btn) btn.classList.remove('is-audio-playing');
      }
    },

    /**
     * Phát âm thanh: Ưu tiên phát MP3 từ server (audioUrl),
     * nếu audioUrl rỗng hoặc tải lỗi thì fallback sang Web Speech API.
     * @param {string|null} audioUrl Đường dẫn file mp3 trên server (VD: /static/voice/cards/abc.mp3)
     * @param {string} fallbackText Chữ Hán cần đọc khi fallback
     * @param {Object} options Tuỳ chọn ({ btnElement, lang, rate })
     */
    play: function (audioUrl, fallbackText, options) {
      options = options || {};
      var btn = options.btnElement || null;

      // Dừng âm thanh trước đó
      this.stop();

      // Nếu có audioUrl hợp lệ (bắt đầu bằng /static hoặc http)
      if (audioUrl && typeof audioUrl === 'string' && audioUrl.trim().length > 0) {
        if (btn) btn.classList.add('is-audio-playing');

        var audio = new Audio(audioUrl.trim());
        this.currentAudio = audio;

        var self = this;
        audio.onended = function () {
          if (btn) btn.classList.remove('is-audio-playing');
          self.currentAudio = null;
        };

        audio.onerror = function (e) {
          console.warn('Audio MP3 play failed, falling back to Web Speech API:', e);
          if (btn) btn.classList.remove('is-audio-playing');
          self.currentAudio = null;
          if (fallbackText) {
            self.speechFallback(fallbackText, options);
          }
        };

        var playPromise = audio.play();
        if (playPromise !== undefined) {
          playPromise.catch(function (err) {
            console.warn('Playback error:', err);
            if (btn) btn.classList.remove('is-audio-playing');
            self.currentAudio = null;
            if (fallbackText) {
              self.speechFallback(fallbackText, options);
            }
          });
        }
      } else if (fallbackText) {
        this.speechFallback(fallbackText, options);
      }
    }
  };

  global.AudioPlayer = AudioPlayer;
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = AudioPlayer;
  }
})(typeof window !== 'undefined' ? window : this);
