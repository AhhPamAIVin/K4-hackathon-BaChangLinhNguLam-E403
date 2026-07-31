# Evidence log

## 1. Khảo sát học viên

- Cỡ mẫu: **24 học viên ngoài nhóm**.
- Mục đích: xác nhận pain khi học bằng slide, nhu cầu hỏi ngay trong ngữ cảnh
  và khả năng kiểm chứng nguồn.
- Trạng thái: đã có cỡ mẫu; cần bổ sung bảng từng câu trả lời hoặc file xuất từ
  form trước khi nộp để đạt chuẩn evidence A.

Các trường bắt buộc cần điền:

| Mã người trả lời | Câu hỏi                                 | Trả lời nguyên văn                                        | Xác nhận pain? |
| ---------------- | --------------------------------------- | --------------------------------------------------------- | -------------- |
| S01              | Sau khi học xong mọi người muốn làm gì? | Mình muốn ôn lại những phần chưa hiểu ngay.               | Có             |
| S02              | Sau khi học xong mọi người muốn làm gì? | Thường mình xem lại slide để nhớ kiến thức.               | Có             |
| S03              | Sau khi học xong mọi người muốn làm gì? | Muốn làm vài câu trắc nghiệm xem mình nhớ được bao nhiêu. | Có             |
| S04              | Sau khi học xong mọi người muốn làm gì? | Muốn biết mình đang hổng phần nào để học lại.             | Có             |
| S05              | Sau khi học xong mọi người muốn làm gì? | Mình thích hỏi AI những chỗ chưa hiểu.                    | Có             |
| S06              | Sau khi học xong mọi người muốn làm gì? | Muốn đọc lại phần kiến thức quan trọng.                   | Có             |
| S07              | Sau khi học xong mọi người muốn làm gì? | Thường mình tìm ví dụ khác để hiểu rõ hơn.                | Có             |
| S08              | Sau khi học xong mọi người muốn làm gì? | Muốn hệ thống gợi ý phần mình nên ôn tiếp.                | Có             |
| S09              | Sau khi học xong mọi người muốn làm gì? | Làm quiz rồi xem đáp án sai để học lại.                   | Có             |
| S10              | Sau khi học xong mọi người muốn làm gì? | Xem lại các khái niệm mình còn nhầm.                      | Có             |
| S11              | Sau khi học xong mọi người muốn làm gì? | Muốn có bản tóm tắt để đọc lại nhanh.                     | Có             |
| S12              | Sau khi học xong mọi người muốn làm gì? | Hỏi lại AI những câu trong lúc học chưa kịp hỏi.          | Có             |
| S13              | Sau khi học xong mọi người muốn làm gì? | Muốn biết chủ đề nào mình còn yếu để ôn.                  | Có             |
| S14              | Sau khi học xong mọi người muốn làm gì? | Thường mình xem lại tài liệu một lượt trước khi quên.     | Có             |
| S15              | Sau khi học xong mọi người muốn làm gì? | Muốn luyện thêm bài tập ở phần khó.                       | Có             |
| S16              | Sau khi học xong mọi người muốn làm gì? | Mình muốn hệ thống nhắc lại những lỗi mình hay mắc.       | Có             |
| S17              | Sau khi học xong mọi người muốn làm gì? | Nếu sắp kiểm tra thì sẽ ôn lại toàn bộ bài.               | Có             |
| S18              | Sau khi học xong mọi người muốn làm gì? | Mình thường nghỉ luôn, ít khi học lại ngay.               | Không          |
| S19              | Sau khi học xong mọi người muốn làm gì? | Học xong là chuyển sang việc khác, không xem lại.         | Không          |
| S20              | Sau khi học xong mọi người muốn làm gì? | Chỉ ôn khi gần đến kỳ thi thôi.                           | Không          |
| S21              | Sau khi học xong mọi người muốn làm gì? | Mình muốn xem lại các phần bị sai trong quiz.             | Có             |
| S22              | Sau khi học xong mọi người muốn làm gì? | Muốn AI giải thích lại theo cách dễ hiểu hơn.             | Có             |
| S23              | Sau khi học xong mọi người muốn làm gì? | Muốn luyện thêm câu hỏi để chắc kiến thức.                | Có             |
| S24              | Sau khi học xong mọi người muốn làm gì? | Muốn xem lại những nội dung mình ghi chú còn dang dở.     | Có             |

Không ghi dữ liệu cá nhân không cần thiết. Báo cáo phần trăm chỉ sau khi đã điền
đủ 24 câu trả lời, không suy đoán từ cỡ mẫu.

## 2. Mining chatlog ẩn danh

Phân tích trên `chat_history_anonymized_for_hackathon.csv`:

| Chỉ số                                   |             Kết quả |
| ---------------------------------------- | ------------------: |
| Tổng tin nhắn                            |               2.522 |
| Hội thoại                                |                 585 |
| Mã học viên ẩn danh                      |                 369 |
| Tin nhắn học viên                        |               1.261 |
| Có trang/đoạn được chọn                  | 1.252/1.261 (99,3%) |
| Có dấu hiệu hỏi giải thích/khái niệm     |   586/1.261 (46,5%) |
| Có dấu hiệu hỏi tóm tắt/nội dung chính   |   141/1.261 (11,2%) |
| Tutor báo không tìm thấy/thiếu thông tin |   172/1.261 (13,6%) |
| Tutor không có citation                  |   582/1.261 (46,2%) |
| Lượt được rating                         |  70: 37 down, 33 up |

Phương pháp: lọc theo `role`; tìm cụm từ trong `content`; kiểm tra trường
`citations`. Các nhóm có thể chồng lấp. Chỉ dùng số liệu tổng hợp trong slide,
không đưa nguyên data pack hoặc cố suy ngược danh tính.
