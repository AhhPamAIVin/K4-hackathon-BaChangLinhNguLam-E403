---
trigger: always_on
---

# PROJECT RULES

## Project Overview

Dự án là một website clone đơn giản.

Mục tiêu:

- Clone giao diện dựa trên thiết kế hoặc website mẫu.
- Giao diện cần gần giống bản gốc.
- Code rõ ràng, dễ đọc và dễ chỉnh sửa.
- Ưu tiên hoàn thành đúng chức năng.
- Không xây dựng kiến trúc phức tạp nếu không cần thiết.

## Rule Routing

Trước khi thực hiện nhiệm vụ, xác định phạm vi công việc.

### Frontend

Nếu nhiệm vụ liên quan đến frontend, phải đọc và tuân thủ:

`.agents/rules/frontend.md`

Bao gồm:

- React component
- HTML, CSS và JavaScript
- Responsive layout
- UI interaction
- Form và client-side validation
- Gọi API từ frontend

### Backend

Nếu nhiệm vụ liên quan đến backend, phải đọc và tuân thủ:

`.agents/rules/backend.md`

Bao gồm:

- API endpoint
- Request và response
- Business logic
- Database
- Authentication
- Server-side validation

Nếu nhiệm vụ liên quan đến cả frontend và backend, phải đọc cả hai file rule.

## General Rules

- Chỉ sửa những file liên quan đến yêu cầu.
- Không tự ý thay đổi cấu trúc dự án.
- Không cài thêm thư viện nếu thư viện hiện có đã đáp ứng được.
- Kiểm tra component hoặc code hiện có trước khi tạo mới.
- Ưu tiên tái sử dụng code.
- Đặt tên biến, hàm và component rõ nghĩa.
- Không viết code phức tạp hơn mức cần thiết.
- Không thêm chức năng ngoài yêu cầu.
- Giữ nguyên các chức năng đang hoạt động.
- Không dùng dữ liệu giả nếu dữ liệu thật đã có trong dự án.
- Sau khi sửa, kiểm tra syntax, import và dependency.

## Workflow

Khi nhận nhiệm vụ:

1. Đọc và hiểu yêu cầu.
2. Xác định nhiệm vụ thuộc frontend, backend hoặc cả hai.
3. Đọc file rule tương ứng.
4. Kiểm tra cấu trúc và code hiện tại.
5. Lập kế hoạch thay đổi ngắn gọn.
6. Thực hiện thay đổi nhỏ nhất cần thiết.
7. Kiểm tra lỗi sau khi sửa.
8. Tóm tắt các file đã thay đổi và nội dung đã thực hiện.