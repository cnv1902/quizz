/**
 * AudioPlayer wrapper for game modules
 */
export const AudioPlayer = (typeof window !== 'undefined' && window.AudioPlayer)
  ? window.AudioPlayer
  : {
      play(url, text, options) {
        if (typeof window !== 'undefined' && window.AudioPlayer) {
          window.AudioPlayer.play(url, text, options);
        }
      },
      stop() {
        if (typeof window !== 'undefined' && window.AudioPlayer) {
          window.AudioPlayer.stop();
        }
      }
    };

export default AudioPlayer;
