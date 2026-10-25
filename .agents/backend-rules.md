# Backend Architecture & Coding Guidelines (FastAPI)

When instructed to write or modify backend logic for this project, you MUST strictly adhere to the layered architecture (Domain-Driven Design) described below. **Do not mix concerns** by writing queries directly in route handlers or putting validation inside ORM models.

## 1. Directory Structure & Responsibilities

- **`app/models/` (SQLAlchemy ORM Models)**
  - Chứa định nghĩa cấu trúc bảng CSDL (Entities). 
  - Tuyệt đối KHÔNG chứa logic nghiệp vụ hay validation request tại đây.
  - Class phải kế thừa từ `Base` (`from app.models.base import Base`).
  
- **`app/schemas/` (Pydantic Models)**
  - Chứa các class DTO (Data Transfer Objects) phục vụ kiểm tra/validate dữ liệu đầu vào (Request) và định dạng dữ liệu đầu ra (Response).
  - BẮT BUỘC áp dụng Mô hình kế thừa (Inheritance Pattern): Tách các trường thành các Class riêng biệt để tái sử dụng.
    - `Class Base` (VD: `ItemBase`): Chứa các trường thông tin cơ bản (Không chứa khóa chính ID).
    - `Class Response` (hoặc `Create`, `Update`): Kế thừa lại `Base` và thêm các trường đặc thù như khóa chính (VD: `ID: int`) hoặc cấu hình `ConfigDict(from_attributes=True)`.

- **`app/crud/` (Database Operations - C.R.U.D)**
  - Chỉ chứa logic truy vấn cơ sở dữ liệu bằng SQLAlchemy (Create, Read, Update, Delete).
  - Tên file thường là `crud_[tên_đối_tượng].py` hoặc `[tên_đối_tượng].py`.
  - Các hàm luôn phải nhận `db: Session` làm tham số đầu tiên. Ví dụ: `def get_item(db: Session, item_id: int)`.
  - **KHÔNG** throw lỗi HTTP (`HTTPException`) tại đây. Chỉ trả về dữ liệu hoặc `None`.
  - **QUY TẮC BẮT BUỘC (Explicit Assignment):** Khi tạo mới hoặc cập nhật bản ghi (1-2 objects) trong hàm CRUD, bắt buộc phải khởi tạo đối tượng bằng cách gán tay từng trường (VD: `HeThongHeSoLopDong(GiaTri_Min=obj_in.GiaTri_Min, ...)`). Tuyệt đối KHÔNG sử dụng cú pháp Dictionary Unpacking (`**obj_in.model_dump()`).
  - **Ngoại lệ cho thao tác hàng loạt (Bulk Operations):** Khi cần cập nhật hoặc thêm mới số lượng lớn bản ghi (hàng trăm/ngàn object), ĐƯỢC PHÉP sử dụng Dictionary truyền thẳng vào `db.bulk_update_mappings()` hoặc `db.bulk_insert_mappings()` để tối ưu tốc độ I/O. Tuy nhiên, các Dictionary này BẮT BUỘC phải được làm sạch bởi Pydantic Schema và xử lý gán giá trị ở tầng Service trước khi truyền xuống CRUD.
  - **QUY TẮC MAPPING TRƯỜNG MỞ RỘNG (Data Mapping):** Tầng CRUD tuyệt đối KHÔNG được import và gọi Pydantic schema (chấm dứt Circular Import). Khi truy vấn dữ liệu từ bảng khác (JOIN) cần đính kèm vào Entity chính, hãy gán giá trị đó trực tiếp vào Model instance bằng `setattr(obj, "field_name", value)` rồi trả về Model instance. Tầng Service sẽ hứng Model này và dùng `Schema.model_validate(obj)` để serialize (Schema phải có `ConfigDict(from_attributes=True)`).
  - **⚠️ CẢNH BÁO LEFT JOIN (Identity Map):** Kỹ thuật gán `setattr` trong vòng lặp (VD: `for row in query.all():`) chỉ an toàn tuyệt đối với các phép JOIN Many-to-One (1 kết quả duy nhất cho mỗi Entity chính). Nếu thực hiện LEFT JOIN One-to-Many, một Model instance có thể lặp lại nhiều lần (do SQLAlchemy Identity Map), khiến `setattr` ghi đè giá trị cũ. Trong trường hợp đó, bạn phải tự gom nhóm (groupby) thủ công hoặc sử dụng tính năng `relationship` thay thế.
  - **QUY TẮC BẮT BUỘC VỀ TRANSACTION & ROLLBACK:** Mọi hàm ghi dữ liệu (Create, Update, Delete, Bulk) BẮT BUỘC phải đặt trong khối `try ... except` và gọi `db.rollback()` ngay lập tức trong khối `except` trước khi re-raise hoặc trả về `None`/`False`. Tuyệt đối không nuốt lỗi mà quên gọi `db.rollback()`.

- **`app/api/v1/endpoints/` (REST API Routers)**
  - Chứa các endpoint API trả về dữ liệu JSON (`@router.get()`, `@router.post()`).
  - Chịu trách nhiệm nhận request, gọi hàm từ thư mục `crud` hoặc `services`, xử lý lỗi (throw `HTTPException` nếu CRUD trả về None) và trả về Pydantic schema.
  - **NGHIÊM CẤM** viết các dòng code truy vấn SQLAlchemy trực tiếp bên trong endpoint.

- **`app/routes/` (UI/HTML Routers)**
  - Chứa các router trả về giao diện HTML qua Jinja2 (`TemplateResponse`) (ví dụ: `ui.py`).

- **`app/services/` (Business Logic & Caching)**
  - Chứa các nghiệp vụ phức tạp đòi hỏi gọi nhiều hàm CRUD liên tiếp, hoặc gọi ra API bên ngoài.

## 2. Quy trình viết mã Backend (Implementation Workflow)
Mỗi khi nhận yêu cầu làm một chức năng Backend mới, bạn phải tuân thủ luồng sau:
1. **Model:** Khai báo cấu trúc bảng trong `app/models/`.
2. **Schema:** Viết các class validate Pydantic trong `app/schemas/`.
3. **CRUD:** Viết các hàm thao tác DB trong `app/crud/`. Bắt buộc dùng Explicit Assignment và có xử lý `db.rollback()` khi lỗi.
4. **Service:** LUÔN LUÔN tạo file Service trong `app/services/` để bọc các hàm CRUD lại, dù là tác vụ đơn giản nhất.
5. **Router/API:** Khai báo endpoint trong `app/api/v1/endpoints/` (JSON). Tầng API BẮT BUỘC phải gọi qua Service, KHÔNG ĐƯỢC gọi trực tiếp hàm trong thư mục CRUD.

## 3. Quy tắc Quản lý Transaction & Rollback (Database Integrity & Leak Prevention)
Để đảm bảo tính toàn vẹn dữ liệu và tránh tình trạng treo Transaction / Connection Leak / `PendingRollbackError`:
1. **Bắt buộc Rollback khi có lỗi ghi:** Mọi thao tác thay đổi dữ liệu (`db.add()`, `db.commit()`, `db.delete()`, `db.bulk_update_mappings()`, `db.bulk_insert_mappings()`) phải có `try ... except`:
   ```python
   try:
       db.add(db_obj)
       db.commit()
       db.refresh(db_obj)
       return db_obj
   except Exception as e:
       db.rollback()
       # Ghi log nếu cần, sau đó raise lỗi hoặc trả về None/False
       raise e
   ```
2. **Hậu quả nếu quên `db.rollback()`:** Nếu có lỗi xảy ra (như vi phạm ràng buộc khóa ngoại, trùng khóa chính, ngắt kết nối...) mà không gọi `db.rollback()`, Session sẽ bị rơi vào trạng thái lỗi (`PendingRollbackError`). Mọi câu lệnh tiếp theo trên Session đó (hoặc Connection được trả về Pool) sẽ bị từ chối thực thi và gây lỗi dây chuyền cho toàn bộ hệ thống.
3. **Thao tác đọc (Read-only):** Với các hàm chỉ `SELECT` (như `get`, `get_all`, `filter`), không cần gọi `commit()` hay `rollback()`, Session sẽ tự động đóng và giải phóng khi kết thúc vòng đời Request nhờ `Depends(get_db)`.
4. **Không chia sẻ `db: Session` qua nhiều luồng song song:** SQLAlchemy Session **không phải** là thread-safe. Tuyệt đối không truyền cùng 1 đối tượng `db` vào các tác vụ chạy song song với `asyncio.gather()` hoặc qua các worker thread khác nhau. Nếu cần xử lý nền/đa luồng, mỗi luồng phải tự mở một session độc lập (VD: `with SessionLocal() as db:`) và luôn có khối `finally: db.close()`.

## 4. Các quy tắc Import
- Luôn sử dụng Absolute Import bắt đầu bằng `app.` (VD: `from app.models.user import User` thay vì `from ..models.user import User`).

## 5. Quy tắc Dữ liệu trả về (No Mock Data)
- Tuyệt đối không được trả về dữ liệu giả định (mock data) cứng trong code API.
- Nếu không lấy được dữ liệu do bảng trống hoặc lỗi, API phải trả về mảng rỗng `[]` (đối với danh sách), giá trị `null`, hoặc mã lỗi HTTP phù hợp để Frontend tự định đoạt trạng thái (Hiển thị "Không có dữ liệu").
