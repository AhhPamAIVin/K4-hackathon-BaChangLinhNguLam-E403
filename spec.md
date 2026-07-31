# AI SPEC — Hỏi đáp có dẫn nguồn ngay trong slide · Nhóm [Điền] · Zone [Điền]

Hướng: [x] A — VLearn  
Loại: [x] Tối ưu tính năng có sẵn

> Các ô `[Điền]` cần dữ liệu thật của nhóm. Quality bar chỉ được coi là đã chốt
> nếu file này được commit trước deadline của khóa.

## §1. User & Job

- Job executor: học viên đang đọc slide trong giờ học hoặc khi tự ôn.
- Core JTBD: Khi gặp một đoạn chưa hiểu, học viên muốn được giải thích ngay
  trong đúng ngữ cảnh và kiểm tra được nguồn, để tiếp tục học mà không phải rời
  khỏi tài liệu hoặc tin mù quáng vào câu trả lời.
- Problem statement: Học viên bị gián đoạn khi không hiểu một đoạn slide; câu
  trả lời hiện tại nhiều lúc thiếu căn cứ hoặc không tìm thấy nội dung.
- Evidence:
  - Khảo sát trực tiếp: **n = 24 học viên**. Kết quả từng câu và tỷ lệ xác nhận:
    `[Điền từ evidence/README.md]`.
  - Mining: 2.522 tin nhắn, 585 hội thoại, 369 mã học viên ẩn danh.
  - 172/1.261 phản hồi tutor báo không tìm thấy/thiếu thông tin.
  - 582/1.261 phản hồi tutor không có citation.
  - Ví dụ/quote ngắn có mã nguồn: `[Điền ít nhất 5 ví dụ, không dán đoạn dài]`.

## §2. Impact & quyết định chọn

| Ứng viên | Bằng chứng | Quyết định |
|---|---|---|
| Hỏi đáp theo đoạn slide, citation mở xem | 1.252/1.261 câu có trang/selection; 582 phản hồi không citation | Chọn làm lát cắt chính |
| Tóm tắt slide | 141/1.261 câu có dấu hiệu hỏi tóm tắt/nội dung chính | Giữ như hành vi hỗ trợ |
| Quiz phát hiện lỗ hổng + ôn tập | Chưa có bằng chứng định lượng trực tiếp từ chatlog | Build như phần mở rộng, cần validation |

Impact đầy đủ theo số người × tần suất × cost mỗi lần: `[Điền từ khảo sát 24
người; không suy đoán số chưa đo]`.

## §3. Giải pháp tương tự đã nghiên cứu

- Chat trong VS Code/Codex: đáng học ở panel bên phải, hội thoại liên tục và
  textarea nhiều dòng; VLearn khác ở grounding theo học liệu và citation.
- Chatbot học tập thông thường: đáng học ở tốc độ hỏi đáp; cần tránh trả lời
  ngoài tài liệu hoặc chỉ hiện tên nguồn không kiểm chứng được.

## §4. Thiết kế

- Lát cắt một câu: Với học viên đang bị kẹt ở một đoạn slide, hệ thống quyết
  định phần học liệu liên quan và trả lời giải thích có citation mở xem được,
  để học viên kiểm chứng rồi tiếp tục học ngay trong màn hình hiện tại.
- Non-goals:
  1. Không trả lời kiến thức tổng quát ngoài học liệu khóa học.
  2. Không thay giảng viên chấm điểm chính thức.
  3. Không suy đoán danh tính hoặc xử lý dữ liệu cá nhân.
  4. Không xây tài khoản/LMS và đồng bộ tiến độ dài hạn.
- Mức prototype: **Working**. Frontend, FastAPI, guardrail, retrieval, model,
  quiz và citation đều chạy thật; storage JSON/JSONL là giới hạn prototype.
- Automation: **augment**. Cost-of-error của kiến thức sai là học sai và mất
  niềm tin; người học vẫn kiểm chứng nguồn và quyết định tiếp theo.

| Nguyên tắc | Áp cụ thể vào prototype |
|---|---|
| G1 — Làm rõ hệ thống làm được gì | Ba tab và thông báo chỉ hỗ trợ học tập |
| G2 — Làm rõ nó làm tốt đến đâu | Nêu rõ câu trả lời dựa trên học liệu |
| G10 — Thu hẹp khi nghi ngờ | Câu mơ hồ được hỏi lại thay vì đoán |
| G9 — Sửa dễ dàng | Có thể bổ sung selection hoặc hỏi tiếp trong lịch sử chat |
| G11 — Giải thích vì sao | Citation mở được mã, nguồn và excerpt |

## §5. Kiểu lỗi — 4 lớp chỗ khó

| Tình huống | Lớp | Hành vi mong muốn | Nguyên tắc |
|---|---|---|---|
| Model tạo mã citation không có trong context | ① Nguồn sự thật | Backend loại citation không hợp lệ | G2/G11 |
| Retrieval không tìm đủ căn cứ | ① Nguồn sự thật | Nói không đủ dữ liệu, không bịa | G10 |
| “Cái này là gì?” không có selection | ② Mơ hồ | Hỏi rõ khái niệm/trang | G10 |
| Selection thiếu file hoặc số trang | ② Mơ hồ | Không tin selection, yêu cầu chọn lại | G10 |
| Hỏi thời tiết hoặc giải trí | ③ Ngoài phạm vi | Từ chối ngắn và hướng về học tập | G1 |
| Yêu cầu lộ system prompt/danh tính | ③ Ngoài phạm vi | Chặn trước model | G1/G10 |
| Giải thích sai một khái niệm gần giống | ④ Domain | Ground bằng transcript và hiện nguồn | G2/G11 |
| Quiz có hơn một đáp án đúng hoặc sai objective | ④ Domain | Validate schema; giải thích và citation | G2/G11 |

Case đáng sợ nhất: câu trả lời nghe hợp lý nhưng gắn citation sai, làm học viên
tin và học sai. Biện pháp: retrieval có metadata, prompt grounding, backend lọc
citation và giao diện mở excerpt.

## §6. Bốn đường đi của trải nghiệm

- Happy: chọn đoạn → hỏi → nhận trả lời → mở citation.
- Low-confidence: câu mơ hồ → hệ thống hỏi lại.
- Failure: không đủ căn cứ → nói rõ giới hạn, không bịa.
- Correction: học viên bổ sung selection/sửa câu → tiếp tục hội thoại.
- Ngoài phạm vi: guardrail chặn scope, injection, privacy và unsafe trước model.
- Domain: quiz có objective, giải thích và citation; câu sai tạo learning gap.

## §7. Kiểm thử

- Golden set: 25 case trong `eval/golden_cases.json`.
- Pass kiểm chứng được:
  - action đúng `block`/`clarify`/`allow`;
  - guardrail code đúng;
  - live mode: case allow có ít nhất 1 citation.
- Quality bar đề xuất nếu vẫn trước deadline: ≥90% toàn bộ bộ test; 100% case
  privacy/prompt injection/unsafe chặn đúng; 100% case allow live có citation.
- Kết quả live mới nhất: **25/25 (100%)**.
- Unit/integration: **16/16 pass**.
- Giới hạn: golden set mới có 3 case allow, chưa đo đầy đủ faithfulness, độ hữu
  ích sư phạm hoặc retrieval precision.

## §8. Phân công & kế hoạch

- Thành viên và phân công: `[Điền giống bảng README.md]`.
- Khảo sát: 24 học viên.
- Validation sau cải tiến: 6 học viên; điền log tại
  `validation/feedback-log.md`.
- Willing users có tên: `[Điền ít nhất 3 tên]`.
- Người giữ log và người dry run: `[Điền]`.

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| Trước validation | Citation mở được nội dung nguồn | Người học cần kiểm chứng thay vì chỉ thấy tên nguồn |
| Trước validation | Sidebar có nút mở lại sau khi đóng | Tránh mất đường quay lại danh sách học liệu |
| Trước validation | Textarea tự giãn nhiều dòng | Cho phép nhập câu hỏi dài |
| Trước validation | Quiz tổng hợp learning gap | Biến điểm số thành hành động ôn tập |
| Sau validation | `[Điền thay đổi từ 6 học viên]` | `[Trỏ tới dòng feedback cụ thể]` |
