# Hướng dẫn công việc — Xây dựng AI Tutor RAG cho VLearn

Tài liệu này mô tả thứ tự làm việc để xây dựng một chatbot có thể trả lời câu hỏi về nội dung bài học từ slide và transcript, phục vụ cho demo hackathon.

## Mục tiêu chính

Xây dựng một chatbot có thể:
- trả lời câu hỏi về một slide cụ thể;
- trả lời câu hỏi về toàn bộ bài học / toàn bộ slide;
- trả lời kèm trích dẫn nguồn (slide hoặc transcript);
- hoạt động tốt trên dữ liệu trong thư mục data/vlearn-pack.

## Nguyên tắc làm việc

1. Dùng dữ liệu trong data/vlearn-pack làm nguồn tin cậy chính.
2. Không đẩy dữ liệu gốc vào repo công khai; chỉ lưu trích dẫn ngắn và kết quả đánh giá.
3. Mỗi bước phải có output rõ ràng trước khi chuyển sang bước tiếp theo.
4. Ưu tiên làm được flow chính trước, sau đó mới tối ưu chất lượng.

---

## Thứ tự làm việc

### Bước 1 — Khảo sát phạm vi và dữ liệu
Mục tiêu: hiểu rõ dữ liệu có sẵn và xác định giới hạn của chatbot.

Công việc:
- Đọc file README của data pack để hiểu cấu trúc dữ liệu.
- Xem nội dung trong thư mục slides/ và transcript/.
- Đọc file chatlog để hiểu các kiểu câu hỏi học viên thường đặt.
- Xác định câu hỏi mà chatbot cần trả lời đầu tiên:
  - “Slide này nói gì?”
  - “Nội dung chính của bài học là gì?”
  - “Giải thích chi tiết về phần X ở slide Y”
  - “So sánh nội dung giữa 2 slide”

Output:
- danh sách use cases chính;
- danh sách tài liệu nguồn sẽ dùng cho RAG.

---

### Bước 2 — Chọn kiểu dữ liệu làm nguồn cho RAG
Mục tiêu: quyết định dùng slide, transcript, hay cả hai làm nguồn trả lời.

Công việc:
- Phân loại dữ liệu:
  - slide: tốt cho câu hỏi ngắn, dễ truy vấn theo trang/khái niệm;
  - transcript: tốt cho câu hỏi cần giải thích sâu hơn.
- Quyết định chiến lược:
  - ưu tiên slide cho câu hỏi theo từng slide;
  - ưu tiên transcript cho câu hỏi toàn bộ bài học và giải thích sâu;
  - nếu cần, kết hợp cả hai.

Output:
- sơ đồ nguồn dữ liệu cho từng loại câu hỏi.

---

### Bước 3 — Xây dựng golden set ban đầu
Mục tiêu: tạo tập câu hỏi mẫu để kiểm tra chatbot từ đầu.

Công việc:
- Lấy từ chatlog và transcript khoảng 20–30 câu hỏi mẫu.
- Chia thành nhóm:
  - câu hỏi về một slide;
  - câu hỏi về toàn bộ bài học;
  - câu hỏi cần giải thích sâu;
  - câu hỏi mơ hồ hoặc cần hỏi lại.
- Ghi lại câu hỏi và kỳ vọng về câu trả lời.

Output:
- file eval/golden_set.json hoặc file markdown chứa câu hỏi mẫu.

---

### Bước 4 — Chuẩn bị dữ liệu cho RAG
Mục tiêu: biến dữ liệu slide/transcript thành đoạn văn có thể truy xuất.

Công việc:
- Trích xuất nội dung slide thành các đoạn ngắn, có metadata như:
  - slide_id
  - title
  - source
  - page
- Trích xuất transcript thành các đoạn chunk theo ngữ cảnh hoặc theo đoạn thoại.
- Gắn metadata đầy đủ để chatbot có thể trích dẫn đúng nguồn.
- Nếu cần, tạo mapping giữa slide và transcript tương ứng.

Output:
- dữ liệu đã chunked và có metadata;
- sơ đồ lưu trữ vector / index.

---

### Bước 5 — Thiết kế kiến trúc chatbot RAG
Mục tiêu: xác định cách chatbot tìm câu trả lời và trả lời.

Công việc:
- Chọn pipeline cơ bản:
  1. Nhận câu hỏi từ người dùng.
  2. Tìm đoạn phù hợp trong kho dữ liệu.
  3. Dùng LLM sinh câu trả lời dựa trên đoạn đã truy xuất.
  4. Trả lời kèm trích dẫn nguồn.
- Xác định cách xử lý các trường hợp:
  - câu hỏi không tìm thấy nguồn phù hợp;
  - câu hỏi quá rộng;
  - câu hỏi cần giải thích theo từng slide.

Output:
- mô tả kiến trúc hệ thống;
- prompt mẫu cho trả lời có trích dẫn.

---

### Bước 6 — Implement prototype chatbot
Mục tiêu: có một phiên bản chạy được với dữ liệu thật.

Công việc:
- Xây dựng pipeline ingest dữ liệu vào vector store hoặc index local.
- Xây dựng endpoint hoặc giao diện chat đơn giản.
- Cho phép người dùng hỏi:
  - về một slide cụ thể;
  - về toàn bộ bài học;
  - về một chủ đề cụ thể.
- Mỗi câu trả lời phải có trích dẫn nguồn.

Output:
- prototype chạy được;
- ít nhất 1 luồng hỏi đáp thực tế hoạt động.

---

### Bước 7 — Tối ưu chất lượng trả lời
Mục tiêu: giảm lỗi và tăng độ tin cậy.

Công việc:
- Dùng golden set để chạy thử.
- Ghi lại lỗi thường gặp:
  - trả lời không đúng slide;
  - trích dẫn sai nguồn;
  - trả lời quá dài hoặc quá chung chung;
  - không biết câu hỏi là về slide hay toàn bộ bài.
- Chọn 1 điểm lỗi đau nhất và sửa trước.

Output:
- danh sách lỗi và cách sửa;
- phiên bản chatbot tốt hơn trước.

---

### Bước 8 — Tối ưu AI tutor hiện có theo dữ liệu chatlog
Mục tiêu: cải thiện điểm weak spot của tutor dựa trên mining chatlog.

Công việc:
- Đọc chatlog để tìm một vấn đề rõ ràng, ví dụ:
  - tutor trả lời quá dài và không trực tiếp vào câu hỏi;
  - tutor không trích dẫn nguồn rõ ràng;
  - tutor lặp lại câu trả lời template;
  - tutor không xử lý câu hỏi liên quan đến nội dung slide.
- Chọn 1 vấn đề và cải thiện cụ thể.
- Đưa quy tắc mới vào prompt hoặc pipeline.

Output:
- một điểm cải thiện đã được triển khai;
- bằng chứng bằng một vài ví dụ trước/sau.

---




- Việc 1: nghiên cứu dữ liệu, mining chatlog, xây golden set.
- Việc 2: chuẩn bị dữ liệu và pipeline RAG.
- Việc 3: build chatbot và prompt trả lời có trích dẫn.


---

### Bước 9 — Thứ tự làm việc cụ thể cho người 1 (chatbot tutor)
Mục tiêu: đảm bảo người 1 làm đúng phần cốt lõi trước khi giao diện và backend hoàn thiện.

Công việc:
1. Xác định 3–5 câu hỏi cốt lõi mà tutor phải trả lời được.
2. Xây dựng golden set đầu tiên với khoảng 10–15 câu hỏi mẫu.
3. Chọn nguồn dữ liệu và chính sách chunking cho slide/transcript.
4. Build prompt cơ bản và logic trả lời có trích dẫn.
5. Chạy thử trên vài câu hỏi mẫu, ghi lại lỗi và sửa trước.
6. Cung cấp API hoặc endpoint cho người 2 dùng trong giao diện.

Output:
- prototype tutor có thể trả lời được ít nhất 1 luồng hỏi đáp chính.

---

### Bước 10 — Đo lường và validate
Mục tiêu: kiểm tra chatbot có đủ tốt cho demo hay không.

Công việc:
- Chạy golden set đã xây.
- Ghi lại câu nào đúng, câu nào sai và vì sao.
- Ưu tiên sửa lỗi lớn nhất trước.
- Nếu có thể, thử với ít nhất 3–5 người ngoài nhóm để lấy phản hồi.

Output:
- bảng kết quả đánh giá;
- danh sách cải tiến tiếp theo.

---

### Bước 11 — Chuẩn bị demo và nộp bài
Mục tiêu: trình bày được sản phẩm rõ ràng và có bằng chứng.

Công việc:
- Chuẩn bị demo ngắn: hỏi về 1 slide, hỏi về toàn bộ bài học, hỏi về một phần khó.
- Ghi lại kết quả thực tế và trích dẫn nguồn.
- Tạo README ngắn mô tả cách chạy prototype.
- Đảm bảo repo chỉ chứa trích dẫn ngắn và kết quả, không đẩy dữ liệu gốc.

Output:
- demo-ready prototype;
- thư mục eval/ và validation/ đủ để chấm điểm.

---

## Phân công cho nhóm 3 người

- Người 1 — chatbot tutor: chịu trách nhiệm về prompt, retrieval, trích dẫn nguồn, golden set và chất lượng trả lời.
- Người 2 — giao diện + backend: chịu trách nhiệm xây API, kết nối frontend với chatbot, và làm trải nghiệm học online.
- Người 3 — AI tạo câu hỏi cuối bài giảng + tổng hợp lỗ hổng: chịu trách nhiệm sinh quiz và đưa ra phân tích cho giảng viên.

---

## Điều cần nhớ

- Hãy bắt đầu từ “câu hỏi người dùng thật” trước, không bắt đầu từ công nghệ.
- Với hackathon, một prototype chạy được và có bằng chứng tốt sẽ mạnh hơn một hệ thống quá hoành tráng nhưng chưa kiểm tra được.
- Nếu gặp lỗi kỹ thuật, ưu tiên làm được một luồng chính trước rồi mới mở rộng.
