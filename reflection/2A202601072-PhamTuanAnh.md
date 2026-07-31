# Reflection — 2A202601072 — Phạm Tuấn Anh

## Vai trò và phần tôi làm

Tôi phụ trách product/spec/evidence, backend và tính năng quiz. Tôi tham gia xác
định lát cắt hỏi đáp có dẫn nguồn ngay trong slide, tổng hợp số liệu mining và
viết các phần JTBD, non-goals, rủi ro, quality bar trong spec. Về kỹ thuật, tôi
xây dựng backend FastAPI, retrieval, guardrail, API hỏi đáp/ôn tập và luồng tạo
quiz bằng AI.

## Một quyết định tôi có thể tự giải thích

Tôi quyết định không tin trực tiếp output của model. Với quiz, model phải trả về
JSON theo schema cố định; backend tiếp tục kiểm tra số câu, bốn lựa chọn khác
nhau, đáp án, giải thích và citation. Citation không thuộc summary được cung cấp
sẽ bị loại. Cách này giảm nguy cơ AI tạo nội dung nghe hợp lý nhưng không có
nguồn thật, đồng thời để người học tự kiểm chứng kết quả.

## AI đã hỗ trợ tôi như thế nào

AI giúp tôi dựng scaffold, đề xuất schema, viết bản nháp test, refactor code và
rà các tình huống như prompt injection, câu hỏi mơ hồ, privacy hoặc ngoài phạm
vi. Tôi vẫn đọc lại code, đối chiếu dữ liệu, chạy test và sửa các giả định không
phù hợp. Tôi nhận ra AI giúp tăng tốc, nhưng người làm phải hiểu toàn bộ pipeline
để kiểm soát và giải thích kết quả.

## Case fail của nhóm và điều tôi học được

Phiên bản đầu retrieval dựa nhiều vào từ khóa nên hoạt động kém khi người học
diễn đạt khác transcript. Nhóm chuyển sang dùng chunk có metadata và embedding,
kết hợp semantic với lexical, đồng thời giới hạn citation trong nguồn đã truy
xuất. Tôi học được rằng API chạy thành công chưa chứng minh RAG tốt; cần đo riêng
retrieval, độ đúng của câu trả lời và citation.

Bộ eval hiện đạt 25/25 nhưng chỉ có ba case hợp lệ và chủ yếu đo routing,
guardrail cùng việc có citation. Vì vậy, kết quả 100% chưa chứng minh đầy đủ chất
lượng sư phạm hoặc faithfulness.

## Nếu làm lại, tôi sẽ thay đổi gì

Tôi sẽ xây bộ eval sớm hơn, bổ sung câu hỏi diễn đạt lại, câu có khái niệm gần
nhau và câu thiếu bằng chứng. Mỗi câu hợp lệ nên được chấm theo retrieval
relevance, answer faithfulness, citation correctness và mức hữu ích. Tôi cũng sẽ
validation với người dùng sớm hơn để ưu tiên thay đổi dựa trên quan sát thật.
