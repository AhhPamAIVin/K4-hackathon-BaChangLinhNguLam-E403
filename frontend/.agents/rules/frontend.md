---
trigger: always_on
---

# FRONTEND RULES

## 1. Main Goal

Frontend chủ yếu sử dụng React để clone giao diện mẫu.

Ưu tiên theo thứ tự:

1. Đúng bố cục.
2. Đúng màu sắc, kích thước và khoảng cách.
3. Đúng typography.
4. Responsive trên desktop, tablet và mobile.
5. Code rõ ràng, dễ đọc và dễ tái sử dụng.

## 2. React Rules

- Sử dụng functional component.
- Sử dụng React Hooks khi cần quản lý state hoặc lifecycle.
- Không sử dụng class component nếu không có yêu cầu đặc biệt.
- Dùng tên component theo PascalCase.
- Dùng tên biến và hàm theo camelCase.
- Mỗi component chỉ nên đảm nhận một chức năng chính.
- Không tạo component quá lớn hoặc chứa quá nhiều logic.
- Tách các phần giao diện lặp lại thành component dùng chung.
- Kiểm tra component hiện có trước khi tạo component mới.
- Đặt component trong thư mục phù hợp với cấu trúc dự án hiện tại.

Ví dụ:

```text
Header.jsx
ProductCard.jsx
LoginForm.jsx
Sidebar.jsx