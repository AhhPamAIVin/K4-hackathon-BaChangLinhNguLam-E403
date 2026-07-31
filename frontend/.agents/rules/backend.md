---
trigger: always_on
---

# BACKEND RULES

## 1. Main Goal

Backend sử dụng FastAPI để phục vụ các chức năng cần thiết cho website clone.

Phạm vi dự án:

- Chỉ chạy local để demo.
- Không sử dụng database.
- Không xây dựng kiến trúc phức tạp.
- Ưu tiên code đơn giản, rõ ràng và dễ chỉnh sửa.

## 2. FastAPI Rules

- Sử dụng FastAPI để tạo API.
- Endpoint nên tuân theo REST convention khi phù hợp.
- Sử dụng `async def` khi endpoint có tác vụ bất đồng bộ.
- Không dùng `async def` nếu bên trong chỉ chạy code đồng bộ nặng.
- Khai báo request và response rõ ràng.
- Sử dụng Pydantic model để validate dữ liệu khi cần.
- Đặt tên endpoint, hàm và model rõ nghĩa.
- Không tạo nhiều layer nếu dự án chưa cần.

Ví dụ:

```text
GET    /api/products
GET    /api/products/{product_id}
POST   /api/products
PUT    /api/products/{product_id}
DELETE /api/products/{product_id}