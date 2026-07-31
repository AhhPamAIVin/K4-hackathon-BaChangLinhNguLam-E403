# Validation sau cải tiến (Mock Data)

> ⚠️ Dữ liệu dưới đây chỉ là dữ liệu minh họa (mock data), không phải kết quả khảo sát thực tế.

- Số người đã thử: **6 học viên ngoài nhóm**.
- Mục tiêu: kiểm tra luồng hỏi từ slide, khả năng mở citation và khả năng tiếp
  tục ôn phần kiến thức hổng.

| Người thử | Task                                     | Quan sát                                                                         | Quote nguyên văn                                               | Mức nghiêm trọng |
| --------- | ---------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------- | ---------------- |
| V01       | Hỏi từ đoạn bôi đen và mở nguồn          | Tìm được đúng nội dung, mở citation thành công, mất vài giây mới để ý nút nguồn. | "À, bấm vào đây là ra đúng slide gốc luôn."                    | Low              |
| V02       | Hỏi từ đoạn bôi đen và mở nguồn          | Trả lời đúng nhưng citation hơi nhỏ nên ban đầu không để ý.                      | "Mình thích có nguồn vì biết AI không tự bịa."                 | Medium           |
| V03       | Thử câu mơ hồ hoặc ngoài phạm vi         | Bot từ chối lịch sự và yêu cầu cung cấp thêm ngữ cảnh.                           | "Nó không đoán bừa, hỏi lại khá hợp lý."                       | Low              |
| V04       | Làm quiz và xem kiến thức hổng           | Quiz hoàn thành nhanh, phần tổng hợp kiến thức còn thiếu dễ hiểu.                | "Nhìn phát biết mình hổng phần nào."                           | Low              |
| V05       | Chuyển từ kết quả quiz sang ôn tập       | Luồng chuyển sang ôn tập tự nhiên, gợi ý đúng chủ đề sai nhiều.                  | "Không phải tự tìm lại tài liệu nữa."                          | Low              |
| V06       | Tự thực hiện luồng chính không hướng dẫn | Hoàn thành toàn bộ luồng, chỉ hơi lúng túng ở bước đầu.                          | "Lần đầu vẫn dùng được, chỉ mất chút thời gian tìm chức năng." | Medium           |

## Tổng hợp

- Chủ đề lặp nhiều nhất:
  - Citation khó nhìn (2/6)
  - Muốn nút "Ôn phần này" nổi bật hơn (2/6)
  - Luồng quiz → ôn tập được đánh giá dễ hiểu (4/6)

- Thay đổi đã làm trước demo:
  - Tăng kích thước nút Citation.
  - Thêm nút **Ôn ngay phần còn yếu** sau khi hoàn thành quiz.
  - Cải thiện thông báo khi câu hỏi nằm ngoài phạm vi tài liệu.

- Điều giữ nguyên và lý do:
  - Giữ cơ chế chỉ trả lời dựa trên tài liệu để hạn chế hallucination.
  - Giữ hiển thị citation ở mọi câu trả lời nhằm tăng độ tin cậy.

- Backlog sau demo:
  - Highlight trực tiếp đoạn tài liệu liên quan khi mở citation.
  - Thêm bộ lọc theo chủ đề khi ôn tập.
  - Hiển thị tiến độ học theo từng chương.

- Hai quote đưa lên slide 5:
  1. "Không phải tự tìm lại tài liệu nữa." — Học viên ẩn danh
  2. "Mình thích có nguồn vì biết AI không tự bịa." — Học viên ẩn danh
