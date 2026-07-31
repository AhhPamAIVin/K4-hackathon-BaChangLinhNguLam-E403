# Evidence log

## 1. Khảo sát học viên

- Cỡ mẫu: **24 học viên ngoài nhóm**.
- Mục đích: xác nhận pain khi học bằng slide, nhu cầu hỏi ngay trong ngữ cảnh
  và khả năng kiểm chứng nguồn.
- Trạng thái: đã có cỡ mẫu; cần bổ sung bảng từng câu trả lời hoặc file xuất từ
  form trước khi nộp để đạt chuẩn evidence A.

Các trường bắt buộc cần điền:

| Mã người trả lời | Câu hỏi | Trả lời nguyên văn | Xác nhận pain? |
|---|---|---|---|
| `[S01–S24]` | `[Điền]` | `[Điền]` | Có/Không |

Không ghi dữ liệu cá nhân không cần thiết. Báo cáo phần trăm chỉ sau khi đã điền
đủ 24 câu trả lời, không suy đoán từ cỡ mẫu.

## 2. Mining chatlog ẩn danh

Phân tích trên `chat_history_anonymized_for_hackathon.csv`:

| Chỉ số | Kết quả |
|---|---:|
| Tổng tin nhắn | 2.522 |
| Hội thoại | 585 |
| Mã học viên ẩn danh | 369 |
| Tin nhắn học viên | 1.261 |
| Có trang/đoạn được chọn | 1.252/1.261 (99,3%) |
| Có dấu hiệu hỏi giải thích/khái niệm | 586/1.261 (46,5%) |
| Có dấu hiệu hỏi tóm tắt/nội dung chính | 141/1.261 (11,2%) |
| Tutor báo không tìm thấy/thiếu thông tin | 172/1.261 (13,6%) |
| Tutor không có citation | 582/1.261 (46,2%) |
| Lượt được rating | 70: 37 down, 33 up |

Phương pháp: lọc theo `role`; tìm cụm từ trong `content`; kiểm tra trường
`citations`. Các nhóm có thể chồng lấp. Chỉ dùng số liệu tổng hợp trong slide,
không đưa nguyên data pack hoặc cố suy ngược danh tính.
