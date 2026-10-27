"""
custom_speech_service.py — Xử lý văn bản song ngữ Trung - Việt và ghép âm thanh liền mạch.
Tự động nhận diện chữ Hán vs tiếng Việt, gán giọng đọc tương ứng (Edge-TTS),
và ghép thành DUY NHẤT 1 FILE MP3 từ đầu đến cuối với mốc thời gian Karaoke.
"""

import os
import re
import asyncio
from typing import List, Dict, Any, Tuple
import edge_tts

# Cấu hình giọng đọc
VOICE_ZH = "zh-CN-XiaoxiaoNeural"  # Giọng tiếng Trung chuẩn Bắc Kinh tự nhiên
RATE_ZH = "-4%"

VOICE_VI = "vi-VN-HoaiMyNeural"    # Giọng tiếng Việt truyền cảm, chuẩn phổ thông
RATE_VI = "-2%"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(BASE_DIR, "static")
CUSTOM_VOICE_DIR = os.path.join(STATIC_DIR, "voice", "custom")


def is_cjk_char(ch: str) -> bool:
    """Kiểm tra ký tự có thuộc dải chữ Hán CJK hay không."""
    code = ord(ch)
    return (
        0x4E00 <= code <= 0x9FFF or
        0x3400 <= code <= 0x4DBF or
        0x20000 <= code <= 0x2A6DF or
        0xF900 <= code <= 0xFAFF
    )


def is_latin_viet_char(ch: str) -> bool:
    """Kiểm tra ký tự chữ cái Latin hoặc Tiếng Việt."""
    return bool(re.match(r'[a-zA-ZàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ]', ch))


def segment_bilingual_text(raw_text: str) -> List[Dict[str, Any]]:
    """
    Phân tách văn bản tự do thành các phân đoạn ngôn ngữ (zh hoặc vi).
    Ví dụ: '你好. Xin chào. 我是阮文章。Tôi là nguyễn văn chương'
    -> [
        { 'id': 1, 'text': '你好.', 'lang': 'zh' },
        { 'id': 2, 'text': 'Xin chào.', 'lang': 'vi' },
        { 'id': 3, 'text': '我是阮文章。', 'lang': 'zh' },
        { 'id': 4, 'text': 'Tôi là nguyễn văn chương', 'lang': 'vi' }
    ]
    """
    text = (raw_text or "").strip()
    if not text:
        return []

    lines = text.splitlines()
    segments = []
    seg_id = 1

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue

        current_chars = []
        current_lang = None

        for ch in line_str:
            if is_cjk_char(ch):
                char_lang = "zh"
            elif is_latin_viet_char(ch):
                char_lang = "vi"
            else:
                char_lang = None  # Dấu câu, khoảng trắng, số...

            if char_lang is not None:
                if current_lang is None:
                    current_lang = char_lang
                    current_chars.append(ch)
                elif char_lang == current_lang:
                    current_chars.append(ch)
                else:
                    # Ngôn ngữ thay đổi (từ Trung sang Việt hoặc ngược lại)
                    chunk = "".join(current_chars).strip()
                    if chunk:
                        segments.append({
                            "id": seg_id,
                            "text": chunk,
                            "lang": current_lang,
                        })
                        seg_id += 1
                    current_chars = [ch]
                    current_lang = char_lang
            else:
                # Ký tự trung tính (dấu chấm, dấu phẩy, khoảng trắng): gắn tiếp vào phân đoạn hiện tại
                current_chars.append(ch)

        # Lưu lại phần còn lại của dòng
        if current_chars and current_lang:
            chunk = "".join(current_chars).strip()
            if chunk:
                segments.append({
                    "id": seg_id,
                    "text": chunk,
                    "lang": current_lang,
                })
                seg_id += 1

    return segments


async def synthesize_and_stitch_article(
    article_id: int,
    user_id: int,
    segments: List[Dict[str, Any]],
) -> Tuple[str, float, List[Dict[str, Any]]]:
    """
    Sinh âm thanh từng phân đoạn bằng Edge-TTS (giọng zh-CN hoặc vi-VN tương ứng),
    ghép thành 1 file MP3 duy nhất, tính toán mốc thời gian Karaoke start_time và end_time.
    Trả về: (audio_url, duration_seconds, updated_segments)
    """
    os.makedirs(CUSTOM_VOICE_DIR, exist_ok=True)
    filename = f"custom_article_{user_id}_{article_id}.mp3"
    file_path = os.path.join(CUSTOM_VOICE_DIR, filename)
    relative_url = f"/static/voice/custom/{filename}"

    combined_audio = bytearray()
    current_time = 0.0
    updated_segments = []

    for seg in segments:
        text = seg["text"].strip()
        lang = seg["lang"]
        voice = VOICE_ZH if lang == "zh" else VOICE_VI
        rate = RATE_ZH if lang == "zh" else RATE_VI

        seg_audio = bytearray()
        duration_ticks = 0

        try:
            communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    seg_audio.extend(chunk["data"])
                elif chunk["type"] == "SentenceBoundary":
                    duration_ticks += chunk.get("duration", 0)
        except Exception as e:
            print(f"[CustomSpeech] Lỗi TTS cho đoạn '{text}': {e}")

        # Tính thời lượng đoạn (1 tick = 100ns -> 10,000,000 ticks = 1s)
        if duration_ticks > 0:
            seg_duration = round(duration_ticks / 10_000_000.0, 2)
        else:
            # Fallback tính theo kích thước dữ liệu mp3 48kbps (6000 bytes/s)
            seg_duration = round(max(0.5, len(seg_audio) / 6000.0), 2)

        start_time = round(current_time, 2)
        end_time = round(current_time + seg_duration, 2)
        current_time = end_time

        updated_segments.append({
            "id": seg["id"],
            "text": text,
            "lang": lang,
            "start_time": start_time,
            "end_time": end_time,
        })

        combined_audio.extend(seg_audio)

    # Ghi toàn bộ dữ liệu audio ghép nối thành 1 file MP3 duy nhất
    with open(file_path, "wb") as f:
        f.write(combined_audio)

    total_duration = round(current_time, 2)
    return relative_url, total_duration, updated_segments
