import csv
import json
import re
from io import BytesIO, StringIO
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
import openpyxl

from app.crud import crud_sentence
from app.models.sentence import Sentence

# Regex kiểm tra ký tự chữ Hán (CJK Unified Ideographs)
HANZI_REGEX = re.compile(r"[\u4e00-\u9fff]")


def contains_hanzi(text: str) -> bool:
    """Kiểm tra chuỗi có chứa chữ Hán hay không."""
    return bool(HANZI_REGEX.search(text or ""))


def get_pinyin_for_sentence(chinese_text: str) -> str:
    """Tự động sinh Pinyin cho câu tiếng Trung."""
    clean_text = (chinese_text or "").strip()
    if not clean_text:
        return ""
    try:
        import pypinyin
        py_list = pypinyin.lazy_pinyin(clean_text, style=pypinyin.Style.TONE)
        return " ".join(py_list)
    except Exception:
        return ""


def segment_sentence(chinese_text: str) -> List[str]:
    """
    Phân tách câu tiếng Trung thành danh sách các khối từ (tokens) để người chơi ghép.
    1. Nếu câu có chứa dấu cách (người dùng cố ý chia cụm: '我 昨天 去 超市'): ưu tiên tách theo dấu cách.
    2. Nếu không có dấu cách:
       - Thử dùng jieba để tách từ vựng tự nhiên.
       - Tách riêng các dấu câu cuối câu (?, !, ., 。, ？, ！).
       - Nếu jieba trả về cả câu hoặc từ quá dài, hoặc câu ngắn: tách từng từ/chữ hợp lý.
    """
    clean_text = (chinese_text or "").strip()
    if not clean_text:
        return []

    # 1. Nếu có khoảng trắng do người dùng chủ động ngắt
    if " " in clean_text:
        tokens = [t.strip() for t in clean_text.split() if t.strip()]
        if tokens:
            return tokens

    # 2. Sử dụng jieba
    try:
        import jieba
        raw_tokens = [w.strip() for w in jieba.cut(clean_text) if w.strip()]
        if raw_tokens and len(raw_tokens) > 1:
            return raw_tokens
    except Exception:
        pass

    # 3. Fallback: tách từng ký tự Hán tự & giữ cụm dấu câu
    return [char for char in clean_text if not char.isspace()]


def get_all(db: Session, set_id: Optional[int] = None, skip: int = 0, limit: Optional[int] = None) -> List[Sentence]:
    return crud_sentence.get_all(db, set_id=set_id, skip=skip, limit=limit)


def get_by_id(db: Session, sentence_id: int) -> Optional[Sentence]:
    return crud_sentence.get_by_id(db, sentence_id)


def create(
    db: Session,
    chinese: str,
    vietnamese: str,
    pinyin: Optional[str] = None,
    tokens: Optional[str] = None,
    order_index: int = 0,
    audio_url: Optional[str] = None,
    set_id: Optional[int] = None,
) -> Sentence:
    # Nếu chưa có tokens, tự động phân tách
    if not tokens:
        token_list = segment_sentence(chinese)
        tokens = json.dumps(token_list, ensure_ascii=False)
    # Nếu chưa có pinyin, tự động sinh
    if not pinyin:
        pinyin = get_pinyin_for_sentence(chinese)

    return crud_sentence.create(
        db,
        chinese=chinese,
        vietnamese=vietnamese,
        pinyin=pinyin,
        tokens=tokens,
        order_index=order_index,
        audio_url=audio_url,
        set_id=set_id,
    )


def bulk_create(db: Session, items: List[dict], set_id: Optional[int] = None) -> List[Sentence]:
    processed_items = []
    for item in items:
        ch = item.get("chinese", "").strip()
        vi = item.get("vietnamese", "").strip()
        if not ch or not vi:
            continue
        py = item.get("pinyin", "").strip() or get_pinyin_for_sentence(ch)
        tok = item.get("tokens", "").strip()
        if not tok:
            tok_list = segment_sentence(ch)
            tok = json.dumps(tok_list, ensure_ascii=False)
        processed_items.append({
            "chinese": ch,
            "vietnamese": vi,
            "pinyin": py,
            "tokens": tok,
            "order_index": item.get("order_index", 0),
            "audio_url": item.get("audio_url"),
            "set_id": item.get("set_id") if item.get("set_id") is not None else set_id,
        })
    return crud_sentence.bulk_create(db, processed_items, set_id=set_id)


def update(db: Session, sentence_id: int, **kwargs) -> Optional[Sentence]:
    if "chinese" in kwargs and kwargs["chinese"]:
        ch = kwargs["chinese"].strip()
        if not kwargs.get("pinyin"):
            kwargs["pinyin"] = get_pinyin_for_sentence(ch)
        if not kwargs.get("tokens"):
            kwargs["tokens"] = json.dumps(segment_sentence(ch), ensure_ascii=False)
    return crud_sentence.update(db, sentence_id, **kwargs)


def delete(db: Session, sentence_id: int) -> bool:
    return crud_sentence.delete(db, sentence_id)


def bulk_delete(db: Session, ids: List[int]) -> int:
    return crud_sentence.bulk_delete(db, ids)


def generate_sample_excel_template() -> bytes:
    """Tạo file Excel mẫu 3 cột: Tiếng Trung | Pinyin | Tiếng Việt."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Câu Ghép Mẫu"

    # Header 3 cột chuẩn
    ws.append(["Tiếng Trung", "Pinyin", "Tiếng Việt"])

    sample_rows = [
        ["你在哪？", "nǐ zài nǎ ？", "Bạn đang ở đâu?"],
        ["今天天气很好。", "jīn tiān tiān qì hěn hǎo 。", "Hôm nay thời tiết rất đẹp."],
        ["我很喜欢学汉语。", "wǒ hěn xǐ huan xué hàn yǔ 。", "Tôi rất thích học tiếng Trung."],
        ["这是我的老师。", "zhè shì wǒ de lǎo shī 。", "Đây là giáo viên của tôi."],
        ["明天你想去哪儿？", "míng tiān nǐ xiǎng qù nǎr ？", "Ngày mai bạn muốn đi đâu?"],
    ]
    for row in sample_rows:
        ws.append(row)

    # Đặt độ rộng cột cho đẹp mắt
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 35

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()


def parse_row_data(row: list) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Nhận diện linh hoạt dòng dữ liệu 2 hoặc 3 cột:
    - 3 cột: [Tiếng Trung, Pinyin, Tiếng Việt] (hoặc tự động phát hiện cột Hán tự)
    - 2 cột: [Tiếng Trung, Tiếng Việt] (Pinyin tự sinh)
    """
    clean_cells = [str(c).strip() if c is not None else "" for c in row if c is not None and str(c).strip() != ""]
    if not clean_cells:
        return None, None, None

    if len(clean_cells) >= 3:
        # 3 cột: Tiếng Trung, Pinyin, Tiếng Việt
        val0, val1, val2 = clean_cells[0], clean_cells[1], clean_cells[2]
        if contains_hanzi(val0):
            return val0, val1, val2
        elif contains_hanzi(val2):
            return val2, val1, val0
        else:
            return val0, val1, val2
    elif len(clean_cells) == 2:
        val0, val1 = clean_cells[0], clean_cells[1]
        if contains_hanzi(val0) and not contains_hanzi(val1):
            return val0, None, val1
        elif contains_hanzi(val1) and not contains_hanzi(val0):
            return val1, None, val0
        else:
            return val0, None, val1
    return None, None, None


def import_from_file(db: Session, filename: str, file_bytes: bytes, set_id: Optional[int] = None) -> List[Sentence]:
    """
    Import câu ghép từ file Excel (.xlsx, .xls) hoặc CSV.
    Hỗ trợ cả 3 cột [Tiếng Trung, Pinyin, Tiếng Việt] hoặc 2 cột [Tiếng Trung, Tiếng Việt].
    """
    lower_name = (filename or "").lower()
    raw_sentences = []

    header_keywords = (
        "tiếng trung", "tieng trung", "chữ hán", "chu han", "hanzi", "chinese",
        "tiếng việt", "tieng viet", "vietnamese", "dịch nghĩa", "nghĩa", "nghia",
        "pinyin", "phiên âm", "phien am"
    )

    if lower_name.endswith((".xlsx", ".xls")):
        wb = openpyxl.load_workbook(filename=BytesIO(file_bytes), read_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            raise ValueError("File Excel không có dữ liệu")

        first_row_str = " ".join(str(c or "").lower() for c in rows[0])
        has_header = any(k in first_row_str for k in header_keywords)
        data_rows = rows[1:] if has_header else rows

        for row in data_rows:
            if not row or all(v is None for v in row):
                continue
            chinese, pinyin, vietnamese = parse_row_data(list(row))
            if chinese and vietnamese:
                raw_sentences.append({
                    "chinese": chinese,
                    "pinyin": pinyin or "",
                    "vietnamese": vietnamese,
                    "set_id": set_id,
                })
    else:
        # File CSV / TXT
        content = file_bytes.decode("utf-8-sig", errors="replace")
        reader = csv.reader(StringIO(content))
        rows = list(reader)
        if not rows:
            raise ValueError("File CSV không có dữ liệu")

        first_row_str = " ".join(str(c or "").lower() for c in rows[0])
        has_header = any(k in first_row_str for k in header_keywords)
        data_rows = rows[1:] if has_header else rows

        for row in data_rows:
            if not row or len(row) < 2:
                continue
            chinese, pinyin, vietnamese = parse_row_data(row)
            if chinese and vietnamese:
                raw_sentences.append({
                    "chinese": chinese,
                    "pinyin": pinyin or "",
                    "vietnamese": vietnamese,
                    "set_id": set_id,
                })

    if not raw_sentences:
        raise ValueError("Không tìm thấy dữ liệu hợp lệ trong file (yêu cầu các cột: Tiếng Trung, [Pinyin], Tiếng Việt)")

    return bulk_create(db, raw_sentences, set_id=set_id)
