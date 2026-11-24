import io
from typing import List, Any, Optional, Dict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def create_styled_excel(
    sheet_title: str,
    headers: List[str],
    data_rows: List[List[Any]],
    col_alignments: Optional[List[str]] = None,
    col_min_widths: Optional[Dict[int, int]] = None,
) -> bytes:
    """
    Tạo file Excel (.xlsx) với định dạng chuẩn chuyên nghiệp cho HanziQuizz:
    - Tiêu đề cột nền đỏ son Á Đông (#C8382D), chữ trắng in đậm, căn giữa.
    - Viền mỏng (#D0D7DE) cho mọi ô.
    - Hỗ trợ căn chỉnh lề (left/center/right) từng cột.
    - Tự động co giãn bề rộng cột dựa trên nội dung (tối thiểu 12, tối đa 70).
    - Cố định dòng tiêu đề (freeze pane) để cuộn trang không bị trôi header.
    - Bật hiển thị gridlines.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_title[:31]  # Excel giới hạn độ dài tên sheet tối đa 31 ký tự

    # Đảm bảo hiển thị lưới đường viền
    ws.views.sheetView[0].showGridLines = True

    # 1. Thêm Header
    ws.append(headers)

    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="C8382D", end_color="C8382D", fill_type="solid")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    thin_border = Border(
        left=Side(style="thin", color="D0D7DE"),
        right=Side(style="thin", color="D0D7DE"),
        top=Side(style="thin", color="D0D7DE"),
        bottom=Side(style="thin", color="D0D7DE"),
    )

    ws.row_dimensions[1].height = 28

    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border

    # 2. Thêm dữ liệu
    data_font = Font(name="Arial", size=10, color="1C1A17")
    
    # Thiết lập căn lề mặc định
    alignments_map = {}
    if col_alignments:
        for idx, align_str in enumerate(col_alignments):
            alignments_map[idx + 1] = align_str

    for row_idx, row_data in enumerate(data_rows, start=2):
        ws.append(row_data)
        ws.row_dimensions[row_idx].height = 22

        for col_idx in range(1, len(row_data) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.font = data_font
            cell.border = thin_border

            align = alignments_map.get(col_idx, "left")
            cell.alignment = Alignment(
                horizontal=align,
                vertical="center",
                wrap_text=(align == "left"),
            )

    # 3. Tính toán và set độ rộng cột tự động
    for col_idx in range(1, len(headers) + 1):
        col_letter = get_column_letter(col_idx)
        header_text = str(headers[col_idx - 1] or "")
        max_len = len(header_text)

        for row_data in data_rows:
            if col_idx - 1 < len(row_data):
                val = row_data[col_idx - 1]
                if val is not None:
                    # Đếm ký tự (tiếng Việt/Hán tự có thể rộng hơn 1 ô tiêu chuẩn)
                    val_str = str(val)
                    line_lens = [len(line) for line in val_str.split("\n")]
                    line_max = max(line_lens) if line_lens else 0
                    if line_max > max_len:
                        max_len = line_max

        min_w = col_min_widths.get(col_idx, 12) if col_min_widths else 12
        calculated_width = max(min_w, min(max_len + 4, 70))
        ws.column_dimensions[col_letter].width = calculated_width

    # 4. Freeze pane dòng 1
    ws.freeze_panes = "A2"

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()
