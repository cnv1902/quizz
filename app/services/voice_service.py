"""
voice_service.py — Dịch vụ tạo giọng đọc tiếng Trung Phổ thông chuẩn (普通话)
Sử dụng edge-tts với giọng Neural rõ ràng, tự nhiên, hỗ trợ sinh file MP3 tĩnh và chạy nền (BackgroundTasks).
"""

import os
import hashlib
import asyncio
from typing import Optional, List
from app.database import SessionLocal

# Cấu hình giọng đọc mặc định
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"  # Giọng phổ thông Bắc Kinh chuẩn, trong trẻo, tự nhiên
DEFAULT_RATE = "-8%"                    # Tốc độ đọc chậm hơn 8% để nghe rõ thanh điệu HSK

DEFAULT_VOICE_VI = "vi-VN-HoaiMyNeural" # Giọng đọc Tiếng Việt truyền cảm, chuẩn phổ thông
DEFAULT_RATE_VI = "-4%"                 # Tốc độ đọc Tiếng Việt tự nhiên


# Thư mục gốc lưu trữ âm thanh
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(BASE_DIR, "static")
VOICE_DIR = os.path.join(STATIC_DIR, "voice")


def get_voice_hash(text: str, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE) -> str:
    """Tạo mã băm MD5 duy nhất dựa trên nội dung chữ, tên voice và tốc độ đọc."""
    normalized = f"{text.strip()}_{voice.strip()}_{rate.strip()}"
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


async def generate_voice_file(
    text: str,
    category: str = "cards",
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
) -> Optional[str]:
    """
    Sinh file MP3 phát âm tiếng Trung và lưu vào thư mục static/voice/{category}/.
    Nếu file đã tồn tại trên đĩa thì trả về URL ngay mà không cần gọi lại TTS (Deduplication).
    Trả về đường dẫn tĩnh công khai: /static/voice/{category}/{hash}.mp3
    """
    clean_text = (text or "").strip()
    if not clean_text:
        return None

    # Đảm bảo thư mục lưu trữ tồn tại
    target_dir = os.path.join(VOICE_DIR, category)
    os.makedirs(target_dir, exist_ok=True)

    file_hash = get_voice_hash(clean_text, voice, rate)
    filename = f"{file_hash}.mp3"
    file_path = os.path.join(target_dir, filename)
    relative_url = f"/static/voice/{category}/{filename}"

    # Nếu file đã tồn tại và kích thước > 0 thì trả về URL ngay
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return relative_url

    try:
        import edge_tts
        communicate = edge_tts.Communicate(clean_text, voice=voice, rate=rate)
        await communicate.save(file_path)
        return relative_url
    except Exception as e:
        print(f"[VoiceService] Loi sinh audio cho '{clean_text}': {e}")
        return None


def generate_voice_file_sync(
    text: str,
    category: str = "cards",
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
) -> Optional[str]:
    """Hàm đồng bộ chạy coroutine generate_voice_file."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Nếu đang trong event loop của FastAPI
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    generate_voice_file(text, category, voice, rate),
                )
                return future.result()
        else:
            return loop.run_until_complete(
                generate_voice_file(text, category, voice, rate)
            )
    except Exception:
        return asyncio.run(generate_voice_file(text, category, voice, rate))


def delete_audio_files(db, audio_urls: List[str]) -> int:
    """
    Xóa các file âm thanh trên đĩa cứng tương ứng với danh sách audio_urls.
    Hàm kiểm tra an toàn:
    1. Chỉ xóa file nằm trong thư mục hợp lệ VOICE_DIR (static/voice).
    2. Chỉ xóa nếu trong database (các bảng Card, Sentence, MeasureWord, GrammarPoint)
       KHÔNG còn bản ghi nào khác đang tham chiếu đến audio_url đó (deduplication check).
    Trả về số lượng file thực tế đã xóa khỏi ổ đĩa.
    """
    if not audio_urls:
        return 0

    from app.models.card import Card
    from app.models.sentence import Sentence
    from app.models.measure_word import MeasureWord
    from app.models.grammar_point import GrammarPoint

    unique_urls = list({u.strip() for u in audio_urls if u and isinstance(u, str) and u.strip()})
    if not unique_urls:
        return 0

    deleted_count = 0
    normalized_voice_dir = os.path.abspath(VOICE_DIR)

    for url in unique_urls:
        clean_url = url.lstrip("/\\")
        abs_path = os.path.abspath(os.path.join(BASE_DIR, clean_url))

        # Kiểm tra an toàn: file phải nằm hoàn toàn trong thư mục VOICE_DIR
        if not abs_path.startswith(normalized_voice_dir):
            continue

        # Kiểm tra xem còn bản ghi nào trong database đang dùng audio_url này không
        if db.query(Card.id).filter((Card.audio_url == url) | (Card.audio_vi_url == url)).first():
            continue
        if db.query(Sentence.id).filter((Sentence.audio_url == url) | (Sentence.audio_vi_url == url)).first():
            continue
        if db.query(MeasureWord.id).filter(MeasureWord.audio_url == url).first():
            continue
        if db.query(GrammarPoint.id).filter(GrammarPoint.audio_url == url).first():
            continue

        # Không còn ai tham chiếu -> Xóa file nếu tồn tại
        try:
            if os.path.exists(abs_path):
                os.remove(abs_path)
                deleted_count += 1
        except Exception as e:
            print(f"[VoiceService] Lỗi khi xóa file audio '{abs_path}': {e}")

    return deleted_count


def delete_audio_file(db, audio_url: Optional[str]) -> bool:
    """Xóa 1 file âm thanh nếu không còn bản ghi nào khác tham chiếu."""
    if not audio_url:
        return False
    return delete_audio_files(db, [audio_url]) > 0



# === Background Tasks Workers ===

def background_generate_voices_for_cards(card_ids: List[int]):
    """Background task: Quét danh sách cards theo ID và sinh file voice MP3 (Trung & Việt)."""
    if not card_ids:
        return

    from app.models.card import Card
    db = SessionLocal()
    try:
        cards = db.query(Card).filter(Card.id.in_(card_ids)).all()
        for card in cards:
            # 1. Voice Tiếng Trung
            if not card.audio_url or not os.path.exists(os.path.join(BASE_DIR, card.audio_url.lstrip("/\\"))):
                url = generate_voice_file_sync(card.hanzi, category="cards")
                if url:
                    card.audio_url = url
            # 2. Voice Tiếng Việt
            if not card.audio_vi_url or not os.path.exists(os.path.join(BASE_DIR, card.audio_vi_url.lstrip("/\\"))):
                url_vi = generate_voice_file_sync(card.vietnamese, category="cards_vi", voice=DEFAULT_VOICE_VI, rate=DEFAULT_RATE_VI)
                if url_vi:
                    card.audio_vi_url = url_vi
        db.commit()
    except Exception as e:
        print(f"[VoiceService] Loi background cards: {e}")
        db.rollback()
    finally:
        db.close()


def background_generate_voices_for_measure_words(mw_ids: List[int]):
    """Background task: Quét danh sách lượng từ và sinh file voice MP3."""
    if not mw_ids:
        return

    from app.models.measure_word import MeasureWord
    db = SessionLocal()
    try:
        items = db.query(MeasureWord).filter(MeasureWord.id.in_(mw_ids)).all()
        for item in items:
            if not item.audio_url or not os.path.exists(os.path.join(BASE_DIR, item.audio_url.lstrip("/\\"))):
                url = generate_voice_file_sync(item.hanzi, category="measure_words")
                if url:
                    item.audio_url = url
        db.commit()
    except Exception as e:
        print(f"[VoiceService] Loi background measure_words: {e}")
        db.rollback()
    finally:
        db.close()


def background_generate_voices_for_grammar(grammar_ids: List[int]):
    """Background task: Quét danh sách điểm ngữ pháp và sinh file voice MP3."""
    if not grammar_ids:
        return

    from app.models.grammar_point import GrammarPoint
    db = SessionLocal()
    try:
        items = db.query(GrammarPoint).filter(GrammarPoint.id.in_(grammar_ids)).all()
        for item in items:
            if not item.audio_url or not os.path.exists(os.path.join(BASE_DIR, item.audio_url.lstrip("/\\"))):
                url = generate_voice_file_sync(item.hanzi, category="grammar")
                if url:
                    item.audio_url = url
        db.commit()
    except Exception as e:
        print(f"[VoiceService] Loi background grammar: {e}")
        db.rollback()
    finally:
        db.close()


def background_generate_voices_for_sentences(sentence_ids: List[int]):
    """Background task: Quét danh sách câu và sinh file voice MP3 (Trung & Việt)."""
    if not sentence_ids:
        return

    from app.models.sentence import Sentence
    db = SessionLocal()
    try:
        items = db.query(Sentence).filter(Sentence.id.in_(sentence_ids)).all()
        for item in items:
            # 1. Voice Tiếng Trung
            if not item.audio_url or not os.path.exists(os.path.join(BASE_DIR, item.audio_url.lstrip("/\\"))):
                url = generate_voice_file_sync(item.chinese, category="sentences")
                if url:
                    item.audio_url = url
            # 2. Voice Tiếng Việt
            if not item.audio_vi_url or not os.path.exists(os.path.join(BASE_DIR, item.audio_vi_url.lstrip("/\\"))):
                url_vi = generate_voice_file_sync(item.vietnamese, category="sentences_vi", voice=DEFAULT_VOICE_VI, rate=DEFAULT_RATE_VI)
                if url_vi:
                    item.audio_vi_url = url_vi
        db.commit()
    except Exception as e:
        print(f"[VoiceService] Loi background sentences: {e}")
        db.rollback()
    finally:
        db.close()


def sync_all_missing_voices():
    """Hàm quét toàn bộ database và tự động sinh voice cho các mục chưa có audio_url hoặc audio_vi_url."""
    from app.models.card import Card
    from app.models.measure_word import MeasureWord
    from app.models.grammar_point import GrammarPoint
    from app.models.sentence import Sentence

    db = SessionLocal()
    counts = {"cards": 0, "cards_vi": 0, "measure_words": 0, "grammar": 0, "sentences": 0, "sentences_vi": 0}
    try:
        # 1. Cards (Trung & Việt)
        cards = db.query(Card).all()
        for c in cards:
            if not c.audio_url:
                url = generate_voice_file_sync(c.hanzi, category="cards")
                if url:
                    c.audio_url = url
                    counts["cards"] += 1
            if not c.audio_vi_url:
                url_vi = generate_voice_file_sync(c.vietnamese, category="cards_vi", voice=DEFAULT_VOICE_VI, rate=DEFAULT_RATE_VI)
                if url_vi:
                    c.audio_vi_url = url_vi
                    counts["cards_vi"] += 1

        # 2. Measure words
        mws = db.query(MeasureWord).filter((MeasureWord.audio_url == None) | (MeasureWord.audio_url == "")).all()
        for m in mws:
            url = generate_voice_file_sync(m.hanzi, category="measure_words")
            if url:
                m.audio_url = url
                counts["measure_words"] += 1

        # 3. Grammar
        gps = db.query(GrammarPoint).filter((GrammarPoint.audio_url == None) | (GrammarPoint.audio_url == "")).all()
        for g in gps:
            url = generate_voice_file_sync(g.hanzi, category="grammar")
            if url:
                g.audio_url = url
                counts["grammar"] += 1

        # 4. Sentences (Trung & Việt)
        sentences = db.query(Sentence).all()
        for s in sentences:
            if not s.audio_url:
                url = generate_voice_file_sync(s.chinese, category="sentences")
                if url:
                    s.audio_url = url
                    counts["sentences"] += 1
            if not s.audio_vi_url:
                url_vi = generate_voice_file_sync(s.vietnamese, category="sentences_vi", voice=DEFAULT_VOICE_VI, rate=DEFAULT_RATE_VI)
                if url_vi:
                    s.audio_vi_url = url_vi
                    counts["sentences_vi"] += 1

        db.commit()
        return counts
    except Exception as e:
        db.rollback()
        print(f"[VoiceService] Loi sync_all_missing_voices: {e}")
        return counts
    finally:
        db.close()

