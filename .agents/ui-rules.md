---
applyTo: "**/*.html,**/*.css,**/*.js,**/*.jsx,**/*.tsx,**/*.vue,**/*.svelte"
---

# Bộ quy tắc thiết kế & xây dựng giao diện — Hệ thống nội bộ Đại học Vinh

Tài liệu này là nguồn quy tắc DUY NHẤT cho mọi giao diện quản trị/nội bộ được tạo ra
(dashboard, form quản lý, bảng dữ liệu, trang cấu hình...). Khi tạo hoặc chỉnh sửa bất kỳ
giao diện nào, luôn đọc và tuân theo file này trước khi viết code. Nếu một yêu cầu trong
hội thoại mâu thuẫn với quy tắc dưới đây, hãy hỏi lại thay vì tự ý phá vỡ quy tắc.

Gốc tham chiếu: giao diện `quan_ly_nhom_lop_hoc_phan.html` (Quản lý nhóm lớp học phần —
Đại học Vinh) đã được xây dựng và kiểm thử theo đúng bộ quy tắc này — dùng làm ví dụ mẫu
khi cần đối chiếu hành vi cụ thể.

## 1. Cấm tuyệt đối — không có ngoại lệ

- **Không dùng gradient** (linear-gradient, radial-gradient...) ở bất kỳ đâu: nền, nút, badge, thanh trạng thái, icon.
- **Không dùng `box-shadow` trang trí.** Ngoại lệ DUY NHẤT: halo mảnh 3px khi input được focus
  (`box-shadow: 0 0 0 3px <màu nhạt>`) — đây là chỉ báo trạng thái, không phải hiệu ứng đổ bóng/nổi khối.
- **Không bo góc quá 8px** cho khối lớn (card, panel, input, button, bảng). Ngoại lệ: badge trạng thái
  dạng pill nhỏ (được phép bo tròn hoàn toàn vì là ký hiệu nhỏ, không phải khối bố cục).
- **Không tạo cảm giác "giao diện AI mặc định":** không phối màu tím-hồng-neon sáo rỗng, không dùng
  font mặc định (Inter/Roboto...) nếu không có lý do, không thêm icon/emoji/hiệu ứng trang trí không
  phục vụ chức năng, không thêm animation/parallax không cần thiết.
- **Không dùng `alert()` / `confirm()` / `prompt()`** mặc định của trình duyệt — luôn dùng toast hoặc
  thành phần UI riêng của hệ thống.
- **Không dùng dữ liệu mẫu vô nghĩa** ("Lorem ipsum", "Item 1", "John Doe", "test test") — luôn sinh dữ
  liệu tiếng Việt thực tế, đúng ngữ cảnh nghiệp vụ của Đại học Vinh (xem mục 8).

## 2. Bảng màu chuẩn — copy nguyên văn, không tự chế hex mới

```css
:root {
  /* Thương hiệu — lấy trực tiếp từ logo Đại học Vinh (#0055AF), KHÔNG đoán hex */
  --brand-800: #0055af; /* topbar, nút primary, toast, nút "Áp dụng" trong dropdown lọc */
  --brand-700: #1568c4; /* hover của brand-800 */
  --brand-900: #003d82; /* active/pressed của brand-800 */

  /* Màu nhấn phụ — dùng cho tương tác thứ cấp, KHÔNG thay thế brand-800 */
  --teal-600: #0e7c7b; /* focus ring, icon sắp xếp/lọc đang active, avatar, viền nút outline phụ */
  --teal-700: #0a5f5e;
  --teal-50: #e6f4f3;

  /* Nền & viền trung tính */
  --bg-page: #eef1f4;
  --bg-panel: #ffffff;
  --bg-subtle: #f4f6f8;
  --bg-subtle-2: #eaedf0;
  --border: #dce3e9;
  --border-strong: #c3cdd5;

  /* Chữ */
  --text-primary: #182430;
  --text-secondary: #5b6b78;
  --text-muted: #96a3ad;

  /* Màu ngữ nghĩa trạng thái — không dùng brand-800 cho các ý nghĩa này */
  --green-600: #1e7a4c;
  --green-50: #e5f3ea; /* thành công / đã xác nhận */
  --amber-600: #a8710d;
  --amber-50: #fbf0da; /* cảnh báo / gần giới hạn / dòng chưa lưu (dirty) */
  --red-600: #b23a2e;
  --red-50: #fbe8e5; /* lỗi / vượt giới hạn */
  --blue-600: #2560a6;
  --blue-50: #e6f0fa; /* đã khoá / đã xử lý xong — khác brand-800 */
}
```

Nếu dự án dùng cho đơn vị khác có logo/màu thương hiệu riêng: lấy màu chủ đạo thật bằng cách
lấy mẫu pixel từ file logo được cung cấp (không đoán hex bằng mắt), chỉ thay nhóm `--brand-*`,
giữ nguyên toàn bộ cấu trúc và vai trò của các token còn lại.

## 3. Typography

- Font chữ chính toàn giao diện: **IBM Plex Sans** (400/500/600), tải qua Google Fonts.
- Font số liệu: **IBM Plex Mono** — dùng cho MỌI cột số, mã (ID/code), giá trị đếm được, kèm
  `font-variant-numeric: tabular-nums` để căn số đẹp như bảng tính.
- Cỡ chữ: 14px nội dung mặc định · 13px trong bảng dữ liệu · 11.5–12px cho label/metadata/badge ·
  15px cho tiêu đề khối. Không dùng cỡ chữ lớn hơn 16px trừ tiêu đề trang.

## 4. Cấu trúc trang chuẩn (thứ tự từ trên xuống)

1. **Topbar** — nền `--brand-800`, chữ trắng. Trái: icon/logo hệ thống + tên module. Phải: ngữ cảnh
   hiện tại (kỳ học/phòng ban/vai trò đang thao tác) + avatar.
2. **Toolbar hành động** — nền trắng, viền dưới `--border`. Đúng **1 nút `primary`** cho hành động
   quan trọng nhất của màn hình, các nút còn lại dùng kiểu `ghost` (viền xám, nền trắng).
3. **Panel bộ lọc** (đóng/mở được) — chia theo **nhóm ý nghĩa** (ví dụ "Phân loại" / "Khoảng giá trị"),
   mỗi nhóm có tiêu đề nhỏ viết hoa. Mỗi nhóm dùng CSS grid với **số cột cố định**, không dùng
   `auto-fit` cho cả panel vì gây lệch hàng khi số trường thay đổi. Trường khoảng số (từ–đến) để độ
   rộng cố định gọn (~220px), không kéo giãn ngang bằng cột select bên cạnh.
4. **Thanh tìm kiếm nhanh** — luôn hiển thị phía trên bảng dữ liệu dù panel lọc đang đóng hay mở.
   Không lặp lại trường đã có sẵn trong panel lọc (một chức năng chỉ nên xuất hiện ở một nơi).
5. **Bảng dữ liệu** — xem mục 6.
6. **Thanh trạng thái footer** — tổng số dòng / đang hiển thị sau lọc / số dòng đã chọn / các số
   tổng hợp liên quan (SUM các cột số quan trọng nhất).

## 5. Thành phần dùng lại

**Nút**

- `primary`: nền `--brand-800`, chữ trắng · hover `--brand-700` · active `--brand-900`.
- `ghost` (mặc định): nền trắng, viền `--border-strong` · hover nền `--bg-subtle`.
- `outline nhấn phụ`: viền `--teal-600`, chữ `--teal-700` — dùng cho hành động dạng "xuất/tải xuống".
- Cao 32px, bo góc 6px, icon svg 14×14 bên trái chữ nếu phù hợp.

**Input / Select**

- Cao 32px, viền 1px `--border-strong`, bo góc 6px.
- Focus: viền `--teal-600` + `box-shadow: 0 0 0 3px var(--teal-50)`.

**Badge trạng thái**

- Dạng pill nhỏ, màu theo mục 2 (xanh lá = tích cực, cam = cảnh báo/tạm, xám = trung tính, xanh
  dương phụ `--blue-*` = đã khoá/hoàn tất). Không dùng `--brand-800` cho badge.

**Toast thông báo**

- Góc dưới-phải màn hình, nền `--brand-800`, chữ trắng, tự ẩn sau ~2.5s. Dùng cho MỌI phản hồi thao
  tác (lưu, xuất, lỗi, cảnh báo) thay cho `alert()`.

**Dropdown lọc kiểu Excel** (bắt buộc cho mọi cột có thể lọc)

- Mở khi bấm icon phễu ở header cột. Có: ô tìm nhanh, checkbox "Chọn tất cả", danh sách checkbox
  từng giá trị duy nhất của cột, nút "Xoá lọc" và "Áp dụng".

## 6. Quy tắc riêng cho bảng dữ liệu (áp dụng khi bảng > 5 cột hoặc cần sửa trực tiếp)

1. Mỗi cột header có **2 icon riêng biệt**: **sắp xếp** (▲▼, bấm đổi vòng tăng → giảm → bỏ sắp xếp,
   chỉ một cột được sắp xếp tại một thời điểm) và **lọc** (icon phễu, mở dropdown như mục 5).
2. Cột chọn dòng (checkbox) + tối đa 2 cột định danh quan trọng nhất phải `position: sticky` khi
   cuộn ngang. Thứ tự z-index bắt buộc: cột ghim ở header > header thường > cột ghim ở thân bảng >
   ô thường — để không bị nội dung khác đè lên khi cuộn cả hai chiều.
3. **Sửa dữ liệu bằng cách nháy đúp vào ô.** Với MỌI ô có thể sửa — kể cả ô có danh sách giá trị gợi
   ý cố định (khoa, trạng thái, hình thức học...) — PHẢI dùng
   `<input type="text" list="...">` kết hợp `<datalist>` (combobox), **tuyệt đối không dùng `<select>`
   cứng để sửa ô**, vì sẽ chặn người dùng nhập giá trị mới ngoài danh sách có sẵn. Cột số dùng
   `<input type="number">`.
4. Dòng vừa sửa nhưng chưa lưu → tô nền `--amber-50` (trạng thái "dirty"). Dòng bị khoá sửa vì lý do
   nghiệp vụ → tô nền `--blue-50`, chặn thao tác nháy đúp và hiện toast giải thích rõ lý do cụ thể —
   không được im lặng bỏ qua thao tác của người dùng.
5. Cột số và mã dùng font mono với `tabular-nums`.
6. Nếu có cột thể hiện tỉ lệ/sức chứa (đăng ký/giới hạn, tồn kho/định mức...) → trực quan hoá bằng
   thanh mini màu theo 3 ngưỡng (xanh = đủ chỗ, cam = gần giới hạn, đỏ = vượt giới hạn), không chỉ
   hiện con số suông.

## 7. Trạng thái tương tác cần xử lý đầy đủ

hover dòng/nút · focus bàn phím rõ ràng · dirty state · locked state · trạng thái rỗng (không có
dữ liệu sau khi lọc → hiện thông báo rõ ràng, không để bảng trắng trơn) · loading (khi có gọi API
thật).

## 8. Kỹ thuật & tự kiểm tra trước khi giao (bắt buộc)

- Nếu không được yêu cầu framework cụ thể: ưu tiên HTML/CSS/JS thuần, gọn nhẹ, không phụ thuộc
  ngoài ngoại trừ Google Fonts.
- Trước khi trả kết quả: tự kiểm tra code không lỗi cú pháp, và các thao tác chính (sắp xếp, lọc,
  sửa ô, lưu, xuất dữ liệu) chạy đúng. Nếu có thể, tự viết một đoạn kiểm thử mô phỏng thao tác để
  xác nhận trước khi báo hoàn thành.

## 9. Khi yêu cầu chưa rõ

Không tự đoán ý nghĩa nghiệp vụ của các trường lạ hoặc chưa rõ nguồn dữ liệu. Nêu rõ giả định đã
dùng, và hỏi lại nếu điều đó ảnh hưởng đáng kể đến logic — thay vì âm thầm bịa ra cho đủ.

## 10. Checklist nhanh trước khi trả kết quả

- [ ] Không gradient / không box-shadow trang trí / không bo góc quá 8px ở khối lớn?
- [ ] Màu dùng đúng token ở mục 2, không tự chế hex mới?
- [ ] Ô sửa dữ liệu có danh sách gợi ý dùng `input + datalist`, không dùng `select` cứng?
- [ ] Panel lọc chia nhóm rõ ràng, không trường nào bị lặp lại ở hai nơi?
- [ ] Cột số/mã dùng font mono?
- [ ] Dữ liệu mẫu là tiếng Việt, thực tế, đủ dòng để kiểm thử?
- [ ] Đã tự kiểm thử các thao tác chính, không lỗi, trước khi báo hoàn thành?

## 11. Kiến trúc thư mục và Mô-đun hóa (Bắt buộc)

Tuyệt đối KHÔNG viết toàn bộ HTML/CSS/JS của một trang vào chung một file duy nhất. Khi tạo mới hoặc tái cấu trúc một trang giao diện, bắt buộc phải tuân thủ kiến trúc phân tách sau:

**1. Cấu trúc Jinja2 Templates (Render phía Server):**

- **Layout chung (`app/templates/base.html`):** Chứa khung HTML tổng thể, nhúng CSS/JS dùng chung.
- **Thành phần dùng chung (`app/templates/layouts/`):** Chứa các file chia nhỏ như `navbar.html`, `sidebar.html`, `footer.html`.
- **Trang nội dung (`app/templates/pages/`):** Chứa file nội dung (content) cụ thể của từng trang (kế thừa `base.html`).

**2. Phân tách CSS (`static/css/`):**

- Chia nhỏ CSS theo vai trò thay vì viết dồn vào một file:
  - `layout.css`: Định dạng khung sườn trang (`.app`, `.app-body`, lưới...).
  - `components.css`: CSS cho các thành phần dùng chung (nút, input, checkbox, bảng...).
  - `sidebar.css`, `navbar.css`, `footer.css`: CSS cho các vùng tương ứng.
  - `content.css`: CSS cho vùng nội dung đặc thù (toolbar, filter...).

**3. Phân tách JavaScript (`static/js/`):**

- **`core/`**: Chứa logic hệ thống dùng chung ở mọi nơi.
  - `constants.js`: Định nghĩa hằng số, cấu hình, URL.
  - `utils.js`: Các hàm công cụ (format số, ngày, tạo chuỗi ngẫu nhiên...).
- **`components/`**: Chứa các khối chức năng UI độc lập.
  - Ví dụ: `toast.js` (hiển thị thông báo), `modal.js`.
- **`pages/`**: Chứa file JS chỉ huy riêng cho duy nhất một trang.
  - Mỗi trang một file (ví dụ: `quan_ly_nhom_lop_hoc_phan.js`). File này sẽ gọi các hàm từ `core` và `components` để xử lý sự kiện DOM cho trang đó.

_Mục đích: Đảm bảo khả năng bảo trì, dễ đọc, và nguyên tắc DRY (Don't Repeat Yourself)._

## 12. Quy tắc viết Javascript cho Trang (Page-level JS)

**12.0 Tách biệt API và Logic Giao diện (Repository Pattern)**

Tuyệt đối tuân thủ việc tách biệt các lời gọi API ra khỏi file logic giao diện (Page JS):

- **API Layer (`static/js/api/`):** Chứa tất cả file Javascript chuyên dụng cho giao tiếp với Backend. Mọi lệnh `fetch()`, xử lý Header, parse JSON, và bắt lỗi HTTP phải đặt ở đây.
- **UI Layer (`static/js/pages/`):** Chỉ gọi các Object/Hàm từ API Layer. Tuyệt đối **không nhúng trực tiếp lệnh `fetch()`** vào file UI Layer.

**12.1 Gom nhóm mã nguồn (Grouping)**

Chia file JS thành các phân khu rõ ràng bằng comment phân cách (ví dụ: `// === 1. STATE ===`). Thứ tự chuẩn:

1. **State & DOM Elements:** Biến trạng thái toàn cục, DOM Node cố định.
2. **Data Processing & Filtering:** Hàm xử lý mảng, sắp xếp, lọc.
3. **Table/HTML Rendering:** Hàm tạo chuỗi HTML, vẽ bảng, phân trang.
4. **UI State Updaters:** Hàm nhỏ cập nhật badge, thống kê footer.
5. **Specific Features:** Khối logic phức tạp lẻ (Inline Editing, Excel Filter...).
6. **Event Listeners Binding:** Gom toàn bộ `addEventListener` vào 1–2 hàm (`bindTableEvents`, `bindStaticEvents`). Tuyệt đối không rải rác gắn sự kiện khắp nơi.
7. **Initialization:** Hàm `init()` duy nhất — gọi API và khởi chạy trang.

**12.2 Bắt buộc chú thích JSDoc**

Mọi hàm phải có block comment `/** ... */` phía trên, giải thích bằng tiếng Việt: mục đích hàm, các tham số, giá trị trả về.

**12.3 Event Delegation**

Tối đa hóa Event Delegation: gắn sự kiện vào phần tử cha (`tbody`, `thead`) và dùng `e.target.closest()`, thay vì vòng lặp gắn sự kiện cho từng thẻ con trong bảng.

## 13. Quy tắc quản lý Dữ liệu Frontend (No Mock Data)

Tuyệt đối không được trả về hoặc gán dữ liệu giả định (mock data) cứng trong code nếu API hoặc nguồn cấp bị lỗi hay không có dữ liệu.
Thay vào đó, phải xử lý lỗi êm mượt và trả về mảng rỗng `[]`, chuỗi rỗng `""`, hoặc null để giao diện tự hiển thị trạng thái "Không có dữ liệu".

## 14. Quy tắc khởi tạo Modal Thêm/Sửa/Xóa (Bắt buộc)

Để đồng nhất toàn bộ UI và tối ưu bảo trì, mọi Modal Thêm/Sửa/Xóa đều bắt buộc phải sử dụng kiến trúc Hybrid Framework đã có:

1. **Giao diện HTML**: Bắt buộc dùng Jinja2 Macro `render_modal` (từ `components/modal_macro.html`) để dựng khung Modal thay vì tự viết lại HTML.
2. **Logic JS**: Bắt buộc kế thừa hoặc sử dụng Class `BaseModal` (từ `static/js/core/modal.js`) để tự động hóa việc mở, đóng (click nút X, ấn phím Escape, click ra ngoài vùng mousedown).
3. Tuyệt đối không dùng JavaScript thuần để generate chuỗi HTML của khung Modal (tránh phình to logic và mất tính trong suốt của Jinja2).

## 15. Quy tắc Xử lý Dropdown và Hiệu ứng Focus (UI Components)

Để tránh các lỗi UI kinh điển (như cắt xén Dropdown bởi Modal, lỗi hiển thị viền Focus lồng nhau), tất cả UI Component (như ComboBox, TagInput) bắt buộc phải tuân thủ:

1. **Dropdown Menu Placement (Kiến trúc Portal)**: Khối HTML hiển thị danh sách xổ xuống (`.dropdown-menu`) tuyệt đối KHÔNG được nhét chung vào cấu trúc của input field hoặc cấu trúc của Modal nội dung (`.modal-body`). Phải dùng JS để **append trực tiếp Dropdown ra lớp phủ ngoài cùng của Modal** (như `.modal-overlay`), sau đó tính toán vị trí bằng `getBoundingClientRect()` dựa theo vị trí tuyệt đối của Input field trên màn hình. Nếu không có Modal, fallback append ra `document.body`.
2. **Hiệu ứng Focus lồng nhau**: Nếu một Component phức tạp sử dụng cấu trúc Hộp ảo bao quanh Input thực bên trong (như TagInput: `div.form-input > input.tag-input-field`), bắt buộc phải:
   - Tước bỏ toàn bộ hiệu ứng Focus/Outline/Ring mặc định của trình duyệt/Tailwind trên Input thực bằng `!important` (`.tag-input-field:focus { outline: none !important; box-shadow: none !important; }`).

## 16. Quy tắc Xử lý SPA (Single Page Application)

Vì hệ thống vận hành theo cơ chế SPA (chỉ nạp lại HTML vùng `#main-content`), mọi trang (page) và thành phần (component) bắt buộc tuân thủ quy trình sau để tránh rò rỉ bộ nhớ (memory leak) và lỗi nạp lại (re-declare):

1. **Quản lý Vòng đời Sự kiện (Event Lifecycle):**
   - Khi một trang gắn sự kiện toàn cục (như `window.addEventListener("ContextReady", ...)`), bắt buộc phải có cơ chế **dọn dẹp sự kiện**.
   - Gán một hàm dọn dẹp vào biến `window.pageCleanup = () => { window.removeEventListener(...) }`. Router của SPA sẽ tự động gọi hàm này trước khi chuyển sang trang khác.
2. **Kế thừa Trạng thái toàn cục (Context/State):**
   - Các sự kiện như `ContextReady` từ Navbar thường chỉ phát ra (emit) một lần duy nhất khi ứng dụng tải lần đầu.
   - Khi điều hướng SPA đến một trang phụ thuộc Context (như Học kỳ/Năm học), bên cạnh việc lắng nghe sự kiện, phải **kiểm tra ngay lập tức trạng thái hiện tại** (ví dụ: `if (typeof navbarState !== "undefined" && navbarState.selectedNamTaiChinh) { ... }`) để tự kích hoạt luồng tải dữ liệu nếu Context đã sẵn sàng từ trước.

3. **Cấu trúc Nạp Script Tránh Xung Đột:**
   - Các script thành phần (Component như DataTable, ComboBox) hoặc API (dùng `const`/`class`) chỉ được nạp **một lần duy nhất**. SPA Router đã có bộ đệm `_loadedScripts` để tự động bỏ qua nếu phát hiện script đã được tải.
   - Trái lại, các file logic của trang (Page-level JS nằm trong `/js/pages/`) luôn được SPA nạp và chạy lại mỗi lần chuyển trang. Vì thế, **bắt buộc** phải bọc toàn bộ code của Page JS trong một **IIFE (Immediately Invoked Function Expression)** dạng `(function() { ... })();` để cô lập biến cục bộ, tránh xung đột biến khi trang được nạp lại nhiều lần.

## 17. Quy tắc khởi tạo Bảng dữ liệu — Tránh gọi API trùng lặp (Bắt buộc)

### Bối cảnh vấn đề

Kiến trúc SPA kết hợp với Navbar phát sự kiện `ContextReady` tạo ra **2 luồng khởi tạo song song**:

- **Luồng A — Tải trang trực tiếp (F5/URL):** `init()` chạy → đọc `navbarState` / `sessionStorage` → gọi `loadData()`. Sau đó Navbar hoàn tất → phát `ContextReady` → `contextReadyHandler` gọi `loadData()` lần 2. **⟹ Gây 2 request API.**
- **Luồng B — Chuyển trang qua SPA Router (bấm menu):** `init()` chạy → gọi `loadData()`. Navbar im lặng, không phát lại `ContextReady`. **⟹ Chỉ 1 request.**

### Giải pháp bắt buộc: Cờ deduplication `lastLoadedNamTaiChinh`

Mọi file JS khởi tạo bảng dữ liệu phụ thuộc `namTaiChinh` đều **bắt buộc** áp dụng cơ chế này.

#### Quy tắc 18.1 — Khai báo cờ

Khai báo biến cờ ngay đầu IIFE, cùng chỗ với các biến state khác:

```js
(function () {
  let userPermissions = null;
  let lastLoadedNamTaiChinh = null; // ← bắt buộc

  // ...
})();
```

Nếu file dùng object `state` tập trung thì thêm vào `state`:

```js
const state = {
  // ...các field hiện tại...
  lastLoadedNamTaiChinh: null, // ← bắt buộc
};
```

#### Quy tắc 17.2 — Hàm tải dữ liệu phải nhận tham số `force`

Hàm `loadData` / `loadTableData` / `init` (tuỳ pattern, xem 18.5) phải có tham số `force = false` và kiểm tra dedup **ngay trước khi gọi API**:

```js
async function loadTableData(namTaiChinh, force = false) {
  if (!namTaiChinh) return;

  // Tránh gọi trùng lặp API nếu đã nạp cùng một năm tài chính
  if (!force && lastLoadedNamTaiChinh === namTaiChinh) {
    return;
  }
  lastLoadedNamTaiChinh = namTaiChinh;

  try {
    // ... gọi API, cập nhật bảng ...
  } catch (error) {
    lastLoadedNamTaiChinh = null; // ← reset để cho phép retry khi gặp lỗi
    // ...
  }
}
```

#### Quy tắc 17.3 — `contextChangedHandler` phải dùng `force = true`

Khi người dùng chủ động đổi năm tài chính, phải buộc load lại bất kể đã nạp hay chưa:

```js
// contextReadyHandler — KHÔNG cần force (dedup xử lý khi F5)
const contextReadyHandler = (e) => {
  loadTableData(e.detail);
};

// contextChangedHandler — BẮT BUỘC force = true
const contextChangedHandler = (e) => {
  loadTableData(e.detail, true);
};
```

> Nếu `contextChangedHandler` có khối `confirmModal` (cảnh báo unsaved changes), **tất cả** lời gọi `loadTableData()` bên trong đó cũng phải truyền `true`.

#### Quy tắc 17.4 — Reset cờ trong `pageCleanup`

Khi SPA chuyển trang, cờ phải được reset để trang kế tiếp có thể tải sạch:

```js
window.pageCleanup = () => {
  window.removeEventListener("ContextReady", contextReadyHandler);
  window.removeEventListener("ContextChanged", contextChangedHandler);
  lastLoadedNamTaiChinh = null; // ← bắt buộc
  window.checkUnsavedChanges = null;
  window.pageCleanup = null;
};
```

#### Quy tắc 17.5 — Phân biệt 2 pattern codebase

**Pattern A** — File tách biệt `init()` (setup bảng) và `loadData(namTaiChinh)` (nạp dữ liệu):

- Áp dụng cờ và dedup vào hàm `loadData` / `loadTableData`.
- Ví dụ: `quan_ly_nhom_lop_hoc_phan.js`, `tra_cuu_nhom_lop_hoc_phan.js`.

**Pattern B** — File dùng `init(namTaiChinh)` gộp cả setup lẫn nạp dữ liệu:

- Áp dụng cờ và dedup vào đầu hàm `init`.
- `contextReadyHandler` gọi `init(e.detail)`, `contextChangedHandler` gọi `init(e.detail, true)`.
- **Không xóa** đoạn kích hoạt thủ công `if (navbarState...) { init(...) }` — đoạn này cần thiết cho SPA Router.
- Ví dụ: `lap_va_ky_danh_sach.js`, `ky_duyet_don_vi.js`, `he_dao_tao_chinh_quy.js`.

#### Quy tắc 17.6 — Kiểm tra cú pháp sau khi sửa

Sau khi sửa bất kỳ file nào, chạy kiểm tra cú pháp:

```powershell
node -c "static/js/pages/admin/<thu_muc>/<ten_file>.js"
```

Không có output = cú pháp hợp lệ. Nếu có `SyntaxError` = phải sửa trước khi commit.

### Checklist nhanh cho mỗi file bảng dữ liệu

- [ ] Đã khai báo `let lastLoadedNamTaiChinh = null`?
- [ ] Hàm tải dữ liệu có tham số `force = false`?
- [ ] Có kiểm tra `if (!force && lastLoadedNamTaiChinh === namTaiChinh) return;`?
- [ ] Có gán `lastLoadedNamTaiChinh = namTaiChinh` trước khi gọi API?
- [ ] Có reset `lastLoadedNamTaiChinh = null` trong `catch` block?
- [ ] `contextChangedHandler` truyền `force = true`?
- [ ] `pageCleanup` reset `lastLoadedNamTaiChinh = null`?
- [ ] Đã chạy `node -c` kiểm tra cú pháp?

## 18. Quy tắc hiển thị Loading Overlay toàn màn hình (PageLoading) (Bắt buộc)

### 18.1 Mục đích và Trải nghiệm người dùng
- Khi trang đang tải dữ liệu ban đầu (F5, nạp lần đầu) hoặc tải dữ liệu lớn khi chuyển kỳ/năm học, chuyển trang qua SPA Router, **bắt buộc** phải kích hoạt màn hình loading phủ mờ toàn bộ giao diện (`#pageLoadingOverlay`).
- Lớp phủ sử dụng `backdrop-filter: blur(8px)` khóa toàn bộ tương tác (click, scroll, nhập liệu) của người dùng để tránh xung đột dữ liệu hoặc bấm nhầm khi dữ liệu chưa sẵn sàng.
- Hiệu ứng bao gồm nhân vật hoạt họa, thanh tiến trình mô phỏng tăng từ 0% đến ~90% kèm dòng text mô tả xoay vòng.

### 18.2 API chuẩn của `window.PageLoading`
Thành phần `static/js/components/loading.js` cung cấp đối tượng toàn cục `PageLoading`:
- `PageLoading.show(title, subtitle)`: Hiển thị overlay, reset tiến trình về 0% và bắt đầu tăng tự động.
  - `title` (string, tùy chọn): Tiêu đề chính, mặc định `'Đang tải trang...'`.
  - `subtitle` (string, tùy chọn): Dòng phụ đề trạng thái.
- `PageLoading.update(progress, text, subtext)`: Cập nhật thủ công phần trăm tiến trình và nội dung thông điệp.
- `PageLoading.hide()`: Hoàn thành tiến trình lên 100%, đổi thông điệp thành `'Hoàn tất dữ liệu!'`, chờ 200ms rồi hiệu ứng mờ dần (fade out) và ẩn hẳn overlay, mở khóa giao diện.

### 18.3 Nguyên tắc bắt buộc `try ... finally` trong Page JS
Mọi hàm nạp dữ liệu bất đồng bộ (`loadData`, `loadTableData`, `init`, ...) **bắt buộc** phải gọi `PageLoading.hide()` trong khối `finally` để đảm bảo overlay luôn được ẩn đi ngay cả khi API gặp lỗi, mạng ngắt quãng, hoặc trả về dữ liệu rỗng. Tuyệt đối không để overlay bị treo vĩnh viễn khóa màn hình.

**Mẫu chuẩn bắt buộc:**
```js
async function loadTableData(namTaiChinh, force = false) {
  if (!namTaiChinh) return;
  if (!force && lastLoadedNamTaiChinh === namTaiChinh) return;
  lastLoadedNamTaiChinh = namTaiChinh;

  // 1. Kích hoạt Loading Overlay
  if (window.PageLoading) {
    PageLoading.show('Đang nạp dữ liệu...', 'Đang đồng bộ dữ liệu nhóm lớp học phần...');
  }

  try {
    const res = await NhomLopHocPhanAPI.getAll({ nam_tai_chinh: namTaiChinh });
    state.records = res?.data || [];
    renderTable();
  } catch (error) {
    console.error('Lỗi khi nạp dữ liệu:', error);
    lastLoadedNamTaiChinh = null;
    showToast('Lỗi khi tải dữ liệu từ máy chủ', 'error');
  } finally {
    // 2. BẮT BUỘC: Ẩn loading trong finally
    if (window.PageLoading) {
      PageLoading.hide();
    }
  }
}
```

### 18.4 Tích hợp với SPA Router
Trong `static/js/core/spa_router.js`, quá trình điều hướng SPA đã tự động kích hoạt `PageLoading.show()` trước khi nạp trang và `PageLoading.hide()` sau khi hoàn tất nạp script trang để đảm bảo chuyển trang mượt mà không bị nháy giao diện.

### Checklist nhanh cho Loading Overlay
- [ ] Đã bọc `PageLoading.show(...)` ngay trước khi gửi request API?
- [ ] Đã đặt `PageLoading.hide()` trong khối `finally` của hàm tải dữ liệu?
- [ ] Thông điệp hiển thị tiếng Việt rõ ràng, đúng ngữ cảnh chức năng của trang?

