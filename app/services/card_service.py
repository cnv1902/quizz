from io import BytesIO
from typing import List, Optional
from sqlalchemy.orm import Session

from app.crud import crud_card, crud_quiz
from app.models.card import Card


def get_cards_for_quiz(db: Session, quiz_id: int) -> List[Card]:
    """Lấy tất cả thẻ của quiz theo order_index."""
    return crud_card.get_by_quiz(db, quiz_id)


def get_cards_priority(db: Session, quiz_id: int, user_id: int) -> List[dict]:
    """Lấy thẻ của quiz sắp xếp theo priority (Bổ Túc mode)."""
    return crud_card.get_by_quiz_with_priority(db, quiz_id, user_id)


def get_all_cards_priority(db: Session, user_id: int) -> List[dict]:
    """Lấy tất cả thẻ hệ thống sắp xếp theo priority."""
    return crud_card.get_all_with_priority(db, user_id)


def create_card(
    db: Session,
    quiz_id: int,
    vietnamese: str,
    pinyin: str,
    hanzi: str,
    order_index: int = 0,
) -> Card:
    """Tạo 1 thẻ mới."""
    # Kiểm tra quiz tồn tại
    if not crud_quiz.get_by_id(db, quiz_id):
        raise ValueError(f"Quiz {quiz_id} không tồn tại")
    return crud_card.create(
        db,
        quiz_id=quiz_id,
        vietnamese=vietnamese.strip(),
        pinyin=pinyin.strip(),
        hanzi=hanzi.strip(),
        order_index=order_index,
    )


def bulk_create_cards(db: Session, quiz_id: int, cards: List[dict]) -> List[dict]:
    """
    Tạo nhiều thẻ cho quiz và trả về danh sách thẻ vừa tạo (kèm ID).
    cards: list of dict với keys: vietnamese, pinyin, hanzi, order_index (optional).
    """
    if not crud_quiz.get_by_id(db, quiz_id):
        raise ValueError(f"Quiz {quiz_id} không tồn tại")

    if not cards:
        raise ValueError("Danh sách thẻ cần thêm không được rỗng")

    current_cards = crud_card.get_by_quiz(db, quiz_id)
    start_order = len(current_cards)

    db_cards = []
    for i, c in enumerate(cards):
        viet = str(c.get("vietnamese", "")).strip()
        pinyin = str(c.get("pinyin", "")).strip()
        hanzi = str(c.get("hanzi", "")).strip()

        # Bỏ qua nếu hoàn toàn rỗng
        if not viet and not hanzi:
            continue

        order_idx = c.get("order_index")
        if order_idx is None:
            order_idx = start_order + i + 1

        db_card = Card(
            quiz_id=quiz_id,
            vietnamese=viet,
            pinyin=pinyin,
            hanzi=hanzi,
            order_index=order_idx,
        )
        db_cards.append(db_card)

    if not db_cards:
        raise ValueError("Không có thẻ nào hợp lệ để thêm")

    db.add_all(db_cards)
    db.commit()
    for card in db_cards:
        db.refresh(card)

    return [
        {
            "id": c.id,
            "quiz_id": c.quiz_id,
            "vietnamese": c.vietnamese,
            "pinyin": c.pinyin,
            "hanzi": c.hanzi,
            "audio_url": c.audio_url,
            "order_index": c.order_index,
        }
        for c in db_cards
    ]


def update_card(db: Session, card_id: int, **fields) -> Optional[Card]:
    """Cập nhật thẻ."""
    card = crud_card.get_by_id(db, card_id)
    if not card:
        return None
    return crud_card.update(db, card, **fields)


def delete_card(db: Session, card_id: int) -> bool:
    """Xóa thẻ."""
    card = crud_card.get_by_id(db, card_id)
    if not card:
        return False
    return crud_card.delete(db, card)


def delete_cards_bulk(db: Session, card_ids: List[int]) -> int:
    """Xóa nhiều thẻ theo danh sách card_id."""
    if not card_ids:
        return 0
    return crud_card.bulk_delete(db, card_ids)



def import_from_excel(db: Session, quiz_id: int, file_bytes: bytes) -> List[Card]:
    """
    Import thẻ từ file Excel (.xlsx, .xls).
    Định dạng: Cột A = Tiếng Việt, Cột B = Pinyin, Cột C = Chữ Hán.
    Dòng đầu (header) bị bỏ qua.
    Trả về danh sách các thẻ vừa import thành công.
    """
    import openpyxl

    if not crud_quiz.get_by_id(db, quiz_id):
        raise ValueError(f"Quiz {quiz_id} không tồn tại")

    wb = openpyxl.load_workbook(filename=BytesIO(file_bytes), read_only=True)
    ws = wb.active

    cards_data = []
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True)):
        if not row or len(row) < 3:
            continue
        viet = str(row[0]).strip() if row[0] is not None else ""
        pinyin = str(row[1]).strip() if row[1] is not None else ""
        hanzi = str(row[2]).strip() if row[2] is not None else ""

        # Bỏ qua dòng trống hoàn toàn
        if not viet and not hanzi:
            continue

        cards_data.append({
            "quiz_id": quiz_id,
            "vietnamese": viet,
            "pinyin": pinyin,
            "hanzi": hanzi,
            "order_index": i,
        })

    wb.close()

    if not cards_data:
        raise ValueError("File Excel không có dữ liệu hợp lệ (cần ít nhất 3 cột: Tiếng Việt, Pinyin, Chữ Hán)")

    return crud_card.bulk_create(db, cards_data)


def import_from_csv(db: Session, quiz_id: int, file_bytes: bytes) -> List[Card]:
    """
    Import thẻ từ file CSV.
    Hỗ trợ UTF-8, UTF-8-SIG (có BOM), UTF-16, và tự động đoán delimiter.
    """
    import csv

    if not crud_quiz.get_by_id(db, quiz_id):
        raise ValueError(f"Quiz {quiz_id} không tồn tại")

    text = None
    for enc in ("utf-8-sig", "utf-8", "utf-16", "latin-1"):
        try:
            text = file_bytes.decode(enc)
            break
        except (UnicodeDecodeError, Exception):
            continue

    if text is None:
        raise ValueError("Không thể đọc mã hóa của file CSV. Vui lòng lưu file với mã hóa UTF-8.")

    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("File CSV trống.")

    sample = lines[0] if len(lines) == 1 else lines[0] + "\n" + lines[1]
    delimiter = ','
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=',;\t')
        delimiter = dialect.delimiter
    except Exception:
        if ';' in sample and sample.count(';') >= sample.count(','):
            delimiter = ';'
        elif '\t' in sample:
            delimiter = '\t'

    reader = csv.reader(lines, delimiter=delimiter)
    rows = list(reader)
    if not rows:
        raise ValueError("File CSV không có dữ liệu hợp lệ")

    data_rows = rows[1:] if len(rows) > 1 else rows

    cards_data = []
    for i, row in enumerate(data_rows):
        if not row or len(row) < 3:
            continue
        viet = str(row[0]).strip()
        pinyin = str(row[1]).strip()
        hanzi = str(row[2]).strip()

        if not viet and not hanzi:
            continue

        cards_data.append({
            "quiz_id": quiz_id,
            "vietnamese": viet,
            "pinyin": pinyin,
            "hanzi": hanzi,
            "order_index": i,
        })

    if not cards_data:
        raise ValueError("File CSV không có dữ liệu thẻ hợp lệ (cần ít nhất 3 cột: Tiếng Việt, Pinyin, Chữ Hán)")

    return crud_card.bulk_create(db, cards_data)


def import_from_file(db: Session, quiz_id: int, filename: str, file_bytes: bytes) -> List[Card]:
    """
    Import thẻ từ file Excel (.xlsx, .xls) hoặc file CSV (.csv).
    Tự động nhận diện định dạng file dựa theo phần mở rộng.
    """
    lower_name = (filename or "").lower()
    if lower_name.endswith((".xlsx", ".xls")):
        return import_from_excel(db, quiz_id, file_bytes)
    elif lower_name.endswith(".csv"):
        return import_from_csv(db, quiz_id, file_bytes)
    else:
        raise ValueError("Chỉ hỗ trợ file Excel (.xlsx, .xls) hoặc file CSV (.csv)")


def generate_sample_excel_template() -> bytes:
    """
    Tạo file Excel mẫu (.xlsx) 3 cột chuẩn chỉnh:
    - Cột A: Tiếng Việt (Nghĩa)
    - Cột B: Pinyin (Phiên âm)
    - Cột C: Chữ Hán
    Định dạng tiêu đề đẹp mắt, độ rộng cột tự căn, hỗ trợ trực tiếp font Unicode tiếng Việt & tiếng Trung.
    """
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "HanziQuizz_Mau"

    # Header
    headers = ["Tiếng Việt", "Pinyin", "Chữ Hán"]
    ws.append(headers)

    # Styling header
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="C8382D", end_color="C8382D", fill_type="solid") # Đỏ son Á Đông
    thin_border = Border(
        left=Side(style='thin', color='D0D7DE'),
        right=Side(style='thin', color='D0D7DE'),
        top=Side(style='thin', color='D0D7DE'),
        bottom=Side(style='thin', color='D0D7DE')
    )

    for col_num in range(1, 4):
        cell = ws.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    # Sample rows
    samples = [
        ("Xin chào", "nǐ hǎo", "你好"),
        ("Cảm ơn", "xièxie", "谢谢"),
        ("Tạm biệt", "zàijiàn", "再见"),
        ("Học sinh", "xuésheng", "学生"),
        ("Giáo viên", "lǎoshī", "老师"),
        ("Trung Quốc", "Zhōngguó", "中国"),
        ("Việt Nam", "Yuènán", "越南"),
        ("Học tập", "xuéxí", "学习"),
    ]

    data_font = Font(name="Arial", size=11)
    for row_idx, row_data in enumerate(samples, start=2):
        ws.append(list(row_data))
        for col_num in range(1, 4):
            c = ws.cell(row=row_idx, column=col_num)
            c.font = data_font
            c.border = thin_border
            if col_num in (2, 3):
                c.alignment = Alignment(horizontal="center", vertical="center")
            else:
                c.alignment = Alignment(horizontal="left", vertical="center")

    # Set column widths & row heights
    ws.column_dimensions['A'].width = 24
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 20
    ws.row_dimensions[1].height = 26

    out = BytesIO()
    wb.save(out)
    return out.getvalue()
