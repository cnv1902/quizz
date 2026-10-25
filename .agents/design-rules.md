# DESIGN_RULES.md — Quy tắc thiết kế UI/CSS cho HanziQuizz

> **Dành cho AI/coding agent.** Đọc toàn bộ file này TRƯỚC khi sửa bất kỳ dòng CSS/HTML/JSX nào. Mục tiêu: biến giao diện hiện tại thành một sản phẩm học tiếng Trung hiện đại, tinh tế, đáng tin cậy — **không có "mùi AI"**.

---

## 0. Bối cảnh sản phẩm

- **Tên:** HanziQuizz — học tiếng Trung qua trò chơi (flashcard, ghép thẻ Pikachu, trắc nghiệm).
- **Ngôn ngữ giao diện:** tiếng Việt. Nội dung học: chữ Hán + pinyin + nghĩa Việt.
- **Người dùng:** học sinh, sinh viên, người đi làm tự học; dùng nhiều trên **điện thoại**.
- **Cảm giác mong muốn:** sạch, tập trung, ấm áp, có chất văn hoá Á Đông nhưng **hiện đại** (kiểu Duolingo × Notion × một tờ giấy thư pháp), không trẻ con quá đà, không "startup template".
- **Nguyên tắc vàng:** _Chữ Hán là nhân vật chính._ Mọi quyết định thiết kế phải làm chữ Hán dễ nhìn, dễ đọc, dễ nhớ hơn.

### Hiện trạng cần sửa (từ trang chủ)

- Hero kiểu template: tiêu đề + đoạn mô tả + 3 số liệu ("Bộ Quiz", "Tổng thẻ", "Xin chào") xếp chung chung.
- Dùng emoji làm icon section (📚, 🔍) → nhìn rẻ, không đồng nhất giữa các thiết bị.
- Số liệu hiển thị "—" (trống) trông như lỗi → cần skeleton/empty state đúng nghĩa.
- Có nguy cơ gradient tím-xanh, card bo tròn đổ bóng, nút pill — những dấu hiệu "AI-generated" điển hình.

---

## 1. Những thứ CẤM (dấu hiệu "AI-generated")

Nếu thấy bất kỳ thứ nào dưới đây trong code, **xoá hoặc thay thế**:

| ❌ Cấm                                                                      | Vì sao                        | ✅ Thay bằng                                  |
| --------------------------------------------------------------------------- | ----------------------------- | --------------------------------------------- |
| Gradient tím → xanh / tím → hồng làm nền hoặc nút                           | Dấu hiệu AI số 1              | Màu phẳng, 1 màu nhấn duy nhất                |
| Emoji làm icon UI (📚🔍🎮✨🚀)                                              | Không đồng bộ, nhìn nghiệp dư | Bộ icon SVG nét đồng nhất (Lucide / Phosphor) |
| Glassmorphism, blur nền, glow neon                                          | Lỗi thời, nặng máy            | Nền đặc, viền mảnh 1px                        |
| Card đổ bóng lớn `box-shadow: 0 20px 60px`                                  | Giả "cao cấp"                 | Viền 1px + bóng rất nhẹ (xem §4)              |
| `border-radius: 9999px` cho mọi thứ                                         | Mất cá tính                   | Radius có hệ thống: 8 / 12 / 16 px            |
| Mọi thứ căn giữa, hero khổng lồ chiếm cả màn hình                           | Template landing page         | Layout app: đi thẳng vào nội dung học         |
| Font Inter/Roboto/system mặc định cho cả chữ Hán                            | Chữ Hán xấu, lệch nét         | Font chữ Hán chuyên dụng (xem §3)             |
| Hiệu ứng `hover: scale(1.05)` + `transition: all`                           | Giật, rẻ                      | Chỉ đổi màu nền/viền, `transition` cụ thể     |
| Animation nhảy, bounce, pulse liên tục                                      | Gây mất tập trung khi học     | Chuyển động ngắn, có mục đích (§7)            |
| Số liệu thống kê khoe khoang ("10,000+ học viên!") khi chưa có dữ liệu thật | Thiếu tin cậy                 | Chỉ hiện số thật của chính người dùng         |
| Câu chữ marketing sáo rỗng ("mỗi màn học là một cuộc phiêu lưu!")           | Giọng AI                      | Câu ngắn, cụ thể, hữu ích (§9)                |
| Dấu chấm than, emoji trong copy                                             | Ồn ào                         | Giọng điềm tĩnh, thân thiện                   |
| Nhiều hơn 1 màu nhấn                                                        | Rối                           | 1 màu nhấn + màu ngữ nghĩa (đúng/sai)         |

---

## 2. Màu sắc

Dùng **CSS variables** ở `:root`, không hard-code màu rải rác. Palette lấy cảm hứng giấy xuyên & mực Á Đông: nền ấm, chữ gần đen, nhấn đỏ son.

```css
:root {
  /* Nền & bề mặt */
  --bg: #faf8f4; /* giấy ấm, KHÔNG dùng trắng tinh #fff làm nền trang */
  --surface: #ffffff; /* card, panel */
  --surface-2: #f3f0ea; /* vùng phụ, input, hover nhẹ */
  --border: #e6e1d8;
  --border-strong: #d3ccbf;

  /* Chữ */
  --text: #1c1a17; /* không dùng #000 */
  --text-2: #5f5a52; /* mô tả, phụ */
  --text-3: #8f897e; /* placeholder, caption */

  /* Màu nhấn duy nhất: đỏ son (朱红) */
  --accent: #c8382d;
  --accent-hover: #ad2f25;
  --accent-soft: #fbedeb; /* nền badge, vùng chọn */
  --on-accent: #ffffff;

  /* Ngữ nghĩa — chỉ dùng cho kết quả đúng/sai/cảnh báo */
  --success: #2f7d4f;
  --success-soft: #e8f3ec;
  --danger: #c8382d; /* trùng accent là chấp nhận được */
  --warning: #b7791f;
  --warning-soft: #fbf3e1;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #15130f;
    --surface: #1e1b16;
    --surface-2: #27231d;
    --border: #332f27;
    --border-strong: #463f34;
    --text: #f2eee6;
    --text-2: #b5aea0;
    --text-3: #857e70;
    --accent: #e2554a;
    --accent-hover: #ec6d63;
    --accent-soft: #3a1f1c;
    --success: #5fb27f;
    --success-soft: #1b2c22;
    --warning: #e0a94a;
    --warning-soft: #33290f;
  }
}
```

**Quy tắc:**

1. Tỉ lệ 80% trung tính / 15% bề mặt / **≤5% màu nhấn**. Nhấn chỉ dành cho: nút chính, trạng thái đang chọn, tiến độ.
2. Độ tương phản chữ/nền **≥ 4.5:1** (chữ lớn ≥ 3:1).
3. Đúng/sai không chỉ dựa vào màu — luôn kèm icon hoặc nhãn chữ (người mù màu).
4. Không thêm màu mới ngoài palette mà không có lý do ghi trong comment.

---

## 3. Typography (QUAN TRỌNG NHẤT với app tiếng Trung)

### Font

```css
:root {
  --font-ui:
    "Be Vietnam Pro", "Inter", system-ui, sans-serif; /* UI tiếng Việt, hỗ trợ dấu tốt */
  --font-han:
    "Noto Serif SC", "Source Han Serif SC", "Songti SC", "SimSun", serif; /* chữ Hán: có chân, giống bản in */
  --font-han-sans:
    "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif; /* chữ Hán dạng gọn, cho UI nhỏ */
  --font-pinyin: "Be Vietnam Pro", "Inter", sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;
}
```

- Dùng Google Fonts với `display=swap`; **subset** Noto SC nếu có thể (nặng).
- Thêm `lang="zh-Hans"` cho thẻ chứa chữ Hán, `lang="vi"` cho trang → trình duyệt chọn glyph đúng.
- **Chữ Hán luôn dùng `--font-han`** khi hiển thị lớn (flashcard, tiêu đề từ); `--font-han-sans` chỉ khi nhỏ < 18px.

### Thang cỡ chữ (rem, base 16px)

| Token         | Cỡ                            | Dùng cho                          |
| ------------- | ----------------------------- | --------------------------------- |
| `--fs-han-xl` | `clamp(4rem, 14vw, 7rem)`     | Chữ Hán trên flashcard            |
| `--fs-han-lg` | `2.5rem`                      | Chữ Hán trong câu hỏi trắc nghiệm |
| `--fs-han-md` | `1.5rem`                      | Chữ Hán trong danh sách           |
| `--fs-h1`     | `clamp(1.75rem, 4vw, 2.5rem)` | Tiêu đề trang                     |
| `--fs-h2`     | `1.375rem`                    | Tiêu đề section                   |
| `--fs-body`   | `1rem`                        | Nội dung                          |
| `--fs-sm`     | `0.875rem`                    | Mô tả phụ                         |
| `--fs-xs`     | `0.75rem`                     | Caption, nhãn                     |

### Quy tắc

- **Pinyin** nằm **ngay trên hoặc dưới** chữ Hán, cỡ ~35–40% chữ Hán, màu `--text-2`, `letter-spacing: 0.02em`.
- **Nghĩa tiếng Việt** là cấp thấp nhất trong thẻ: `--fs-body`, `--text`.
- Tiêu đề: `font-weight: 600`, `letter-spacing: -0.01em`, `line-height: 1.2`. Nội dung: `line-height: 1.6`.
- Chỉ dùng 2 weight chính: **400** và **600**. Không dùng 800/900.
- Số liệu (điểm, streak): `font-variant-numeric: tabular-nums`.
- Độ rộng đoạn văn tối đa `65ch`.

---

## 4. Không gian, bo góc, đổ bóng

```css
:root {
  /* Spacing: bội số của 4 */
  --s-1: 4px;
  --s-2: 8px;
  --s-3: 12px;
  --s-4: 16px;
  --s-5: 24px;
  --s-6: 32px;
  --s-7: 48px;
  --s-8: 64px;

  /* Radius: chỉ 3 mức */
  --r-sm: 8px;
  --r-md: 12px;
  --r-lg: 16px;

  /* Shadow: rất nhẹ, chỉ 2 mức */
  --shadow-1: 0 1px 2px rgba(28, 26, 23, 0.06);
  --shadow-2: 0 4px 12px rgba(28, 26, 23, 0.08);
}
```

- **Mặc định card = nền `--surface` + viền `1px solid var(--border)`**, không bóng. Chỉ dùng `--shadow-1` khi cần nổi (menu, popup: `--shadow-2`).
- Khoảng cách giữa các section ≥ `--s-7`. Padding card: `--s-5` (desktop), `--s-4` (mobile).
- Không dùng giá trị px lạ (13px, 17px, 23px…). Chỉ dùng token.
- Lưới: tối đa `1120px`, gutter `--s-5`; card bộ quiz: `grid-template-columns: repeat(auto-fill, minmax(260px, 1fr))`.

---

## 5. Component

### 5.1 Header / điều hướng

- Cao 56–64px, nền `--bg`, viền dưới `1px var(--border)`, **không** đổ bóng, **không** blur.
- Trái: logo + tên "HanziQuizz" (weight 600). Phải: tìm kiếm, tiến độ, avatar/tên người dùng.
- Mobile: thanh tab dưới cùng (4–5 mục) thay cho hamburger khi có thể.

### 5.2 Trang chủ (thay thế hero kiểu template)

Bỏ hero khổng lồ. Bố cục mới, từ trên xuống:

1. **Lời chào gọn** (1 dòng): "Chào {tên}, hôm nay ôn tiếp nhé." + nút **"Tiếp tục học"** (nút chính, đưa thẳng vào bộ đang học dở).
2. **Dải số liệu của chính người dùng** (3 ô nhỏ, viền mảnh): Chuỗi ngày học · Từ đã thuộc · Cần ôn hôm nay. Chưa có dữ liệu → hiện `0`, **không** hiện "—".
3. **Chế độ chơi** (3 thẻ ngang): Flashcard · Ghép thẻ Pikachu · Trắc nghiệm — mỗi thẻ có icon SVG, tên, mô tả 1 dòng.
4. **Bộ Quiz** — ô tìm kiếm + lưới card bộ từ (xem 5.3).

### 5.3 Card bộ Quiz

```
┌──────────────────────────┐
│ HSK 1                    │  ← nhãn nhỏ (badge --accent-soft)
│ Chào hỏi cơ bản          │  ← tiêu đề, 600
│ 你好  ·  谢谢  ·  再见    │  ← 3 từ mẫu, font Hán, --text-2
│ ▓▓▓▓▓░░░░░  12/30        │  ← thanh tiến độ mảnh 4px
└──────────────────────────┘
```

- Nền `--surface`, viền `--border`, radius `--r-md`. Hover: viền `--border-strong` + `translateY(-1px)`. Focus-visible: outline 2px `--accent`.
- Toàn bộ card là một thẻ `<a>`/`<button>` (vùng bấm lớn).

### 5.4 Flashcard (màn quan trọng nhất)

- Thẻ ở giữa, tỉ lệ ~ `3 / 4` (mobile) hoặc `4 / 3` (desktop), `max-width: 520px`, radius `--r-lg`, viền `--border-strong`, nền `--surface`.
- Mặt trước: chữ Hán `--fs-han-xl` căn giữa, hint nhỏ "Chạm để lật" `--text-3`.
- Mặt sau: pinyin → nghĩa Việt → câu ví dụ (nếu có). Nút phát âm (icon loa) góc trên phải.
- Lật thẻ: `transform: rotateY(180deg)`, `300ms`, `cubic-bezier(.2,.7,.2,1)`; tôn trọng `prefers-reduced-motion`.
- Dưới thẻ: 2 nút cùng cỡ **"Chưa nhớ"** (viền) và **"Đã nhớ"** (nền accent). Phím tắt: `Space` lật, `←` / `→` chấm.
- Phía trên: thanh tiến độ mảnh + "7 / 20".

### 5.5 Trắc nghiệm

- Câu hỏi: chữ Hán `--fs-han-lg` trên cùng, 4 đáp án xếp **dọc** (mobile) hoặc lưới 2×2 (desktop), mỗi đáp án cao ≥ 52px.
- Chọn đúng: viền + nền `--success` / `--success-soft` + icon ✓ (SVG). Sai: `--danger` + icon ✕ và **hiện luôn đáp án đúng**.
- Không dùng rung lắc (shake) mạnh; chỉ đổi màu 150ms.

### 5.6 Ghép thẻ Pikachu

- Ô thẻ vuông, radius `--r-sm`, nền `--surface`, viền `--border`; chữ Hán trong ô dùng `--font-han-sans`.
- Ô đang chọn: viền 2px `--accent` + nền `--accent-soft`. Đường nối: nét 3px `--accent`, bo đầu.
- Ghép đúng: ô mờ dần 200ms rồi biến mất; ghép sai: chớp viền `--danger` 150ms.
- Popup thắng/thua: modal giữa màn hình, nền `--surface`, radius `--r-lg`, overlay `rgba(28,26,23,.5)` (không blur), nút chính + nút phụ.

### 5.7 Nút

| Loại      | Style                                                                    |
| --------- | ------------------------------------------------------------------------ |
| Primary   | nền `--accent`, chữ `--on-accent`, radius `--r-sm`, cao 44px, weight 600 |
| Secondary | nền trong suốt, viền `--border-strong`, chữ `--text`                     |
| Ghost     | không viền, hover nền `--surface-2`                                      |

- Mỗi màn hình **chỉ 1 nút primary**. Vùng bấm tối thiểu **44×44px**.
- Disabled: `opacity: .5; cursor: not-allowed`.

### 5.8 Ô tìm kiếm & input

- Nền `--surface`, viền `--border`, radius `--r-sm`, cao 44px, icon kính lúp SVG bên trái.
- Focus: viền `--accent` + `box-shadow: 0 0 0 3px var(--accent-soft)`. Không đổi layout khi focus.

### 5.9 Trạng thái rỗng / đang tải / lỗi

- **Loading:** skeleton cùng kích thước nội dung thật (nền `--surface-2`, shimmer rất nhẹ). Không dùng spinner xoay to giữa màn hình.
- **Rỗng:** icon SVG nhỏ + 1 câu giải thích + 1 hành động ("Chưa có bộ nào. Tạo bộ đầu tiên").
- **Lỗi:** thông báo ngắn, nói rõ chuyện gì + nút "Thử lại". Không hiện stack trace.

---

## 6. Icon & hình ảnh

- Dùng **một** bộ icon SVG nét đồng nhất (Lucide khuyên dùng), `stroke-width: 1.75`, cỡ 20px (UI) / 24px (nổi bật), màu `currentColor`.
- Không emoji trong UI. Không ảnh stock người cười. Minh hoạ (nếu có): nét đơn giản 1–2 màu theo palette, ví dụ hoạ tiết mây/sóng thanh hải rất nhạt (`opacity ≤ .06`) ở nền hero, **không** chồng lên chữ.
- Logo: giữ file hiện tại, hiển thị cao 28–32px, không thêm hiệu ứng.

---

## 7. Chuyển động

- Thời lượng: `120–200ms` cho phản hồi nhỏ, `250–350ms` cho lật thẻ / modal.
- Easing: `cubic-bezier(.2,.7,.2,1)`. **Cấm** `transition: all`; liệt kê đúng thuộc tính (`color, background-color, border-color, transform, opacity`).
- Chỉ animate `transform` và `opacity` cho hiệu năng.
- Bắt buộc:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

- Không có animation lặp vô hạn trên màn đang học.

---

## 8. Responsive & truy cập

- **Mobile-first.** Test ở 360px, 390px, 768px, 1280px.
- Breakpoint: `640px`, `1024px`. Không có cuộn ngang ở bất kỳ cỡ nào.
- Thanh tương tác chính (nút lật/chấm) nằm vùng ngón cái (nửa dưới màn hình) trên mobile.
- Đầy đủ: `:focus-visible` rõ ràng, nhãn `aria-label` cho nút icon, thứ tự Tab hợp lý, `alt` cho ảnh, `<html lang="vi">`.
- Dùng `100dvh` thay `100vh` trên mobile; chừa `env(safe-area-inset-bottom)` cho tab bar.

---

## 9. Giọng văn (copywriting)

- Ngắn, rõ, điềm tĩnh, xưng "bạn". Không dấu chấm than liên tiếp, không emoji.
- ❌ "Khám phá chữ Hán qua các trò chơi tương tác. Mỗi màn học là một cuộc phiêu lưu!"
- ✅ "Học chữ Hán mỗi ngày 10 phút. Lật thẻ, ghép cặp, làm trắc nghiệm."
- Nút: động từ cụ thể — "Tiếp tục học", "Ôn 12 từ", "Làm lại" (không dùng "Bắt đầu ngay!!!").
- Tiêu đề section không kèm emoji: "Bộ Quiz" chứ không phải "📚 Bộ Quiz".
- Thông báo kết quả trung tính: "Đúng rồi" / "Chưa đúng — đáp án là 你好".

---

## 10. Cách triển khai (quy trình cho AI)

1. **Không đập đi xây lại logic.** Chỉ sửa lớp trình bày (CSS, markup, class). Không đổi API, route, tên biến JS, ID mà script đang dùng.
2. Tạo/chuẩn hoá một file `tokens.css` (hoặc khối `:root`) chứa toàn bộ biến ở §2–§4, import trước mọi CSS khác.
3. Thay dần theo thứ tự: **tokens → typography → header → trang chủ → card bộ quiz → flashcard → trắc nghiệm → Pikachu → trạng thái rỗng/lỗi**.
4. Loại bỏ mọi màu/px hard-code, thay bằng biến. Gộp CSS trùng lặp, xoá rule không dùng.
5. Thay emoji bằng SVG; thay `transition: all`; xoá gradient/blur/bóng nặng.
6. Sau mỗi bước, tự kiểm tra bằng checklist §11 rồi mới sang bước tiếp.
7. Nếu một yêu cầu trong file này mâu thuẫn với chức năng đang chạy, **giữ chức năng**, ghi chú vào PR/commit và đề xuất cách sửa.
8. Với dự án có framework (React/Jinja2/…): đặt style theo component, tái sử dụng class tiện ích; không inline style trừ giá trị động (ví dụ % tiến độ).

---

## 11. Checklist nghiệm thu (phải đạt hết)

**Không còn dấu hiệu AI**

- [ ] Không gradient tím/xanh, không glassmorphism, không glow
- [ ] Không emoji trong UI và copy
- [ ] Không hero khổng lồ căn giữa kiểu landing template
- [ ] Không số liệu giả / "—" trống nhìn như lỗi
- [ ] Chỉ 1 màu nhấn (đỏ son) + màu ngữ nghĩa

**Chất lượng chữ Hán**

- [ ] Chữ Hán dùng font Noto Serif SC (hoặc fallback), `lang="zh-Hans"`
- [ ] Chữ Hán trên flashcard đủ lớn, không bị cắt, không tràn
- [ ] Pinyin và nghĩa Việt đúng thứ bậc thị giác

**Hệ thống**

- [ ] Mọi màu/khoảng cách/bo góc đến từ token
- [ ] Radius chỉ 8/12/16; bóng chỉ 2 mức
- [ ] Không còn `transition: all`

**Trải nghiệm**

- [ ] Mỗi màn có đúng 1 nút primary rõ ràng
- [ ] Vùng bấm ≥ 44px; không cuộn ngang ở 360px
- [ ] Có skeleton, empty state, error state
- [ ] Dark mode hiển thị đúng
- [ ] Lighthouse Accessibility ≥ 95, tương phản đạt AA
- [ ] `prefers-reduced-motion` được tôn trọng

---

## 12. Tham chiếu phong cách (để định hướng, không sao chép)

- **Duolingo:** vòng lặp học ngắn, phản hồi đúng/sai rõ ràng (nhưng bớt màu sắc và mascot).
- **Notion / Linear:** viền mảnh, khoảng trắng rộng, typography sạch.
- **Anki / Pleco:** tôn trọng chữ Hán, mật độ thông tin hợp lý.
- **Giấy & mực thư pháp:** nền ngà ấm, đỏ son làm dấu ấn (như con dấu 印章) — dùng tiết chế.

> Khi phân vân giữa "đẹp hơn" và "dễ học hơn" → chọn **dễ học hơn**.
