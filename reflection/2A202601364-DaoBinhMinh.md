# Reflection — 2A202601364 — Đào Bình Minh

## Vai trò và phần tôi làm

Tôi phụ trách phần retrieval/embedding của chatbot RAG: thiết kế lại cách lưu và dùng
embedding cache (`data/embedding_cache.json`, `embeddings.py`), và cách chia văn bản
thành chunk (`chunk_text()` trong `chatbot.py`). Cụ thể đã làm:

- Đổi cache embedding từ chỗ chỉ lưu `hash` + `embedding` sang lưu thêm `source`,
  `chunk_type`, `page`, `text` — để cache tự đủ dữ liệu làm nguồn truy hồi, không phải
  parse lại transcript/slide gốc mỗi lần chạy.
- Đổi `chunk_text()` từ chia theo đoạn văn (paragraph, không đều, không overlap) sang
  sliding window cố định 200–900 ký tự, overlap 100 ký tự giữa 2 chunk liên tiếp.
- Viết lại `precompute_embeddings.py` để tự backfill field mới cho cache cũ (không tốn
  API call nếu nội dung chunk không đổi) và tự xoá (`prune_cache`) các chunk_id không
  còn tồn tại trong tài liệu gốc.
- Push kết quả lên branch `Dao_Binh_Minh` của repo nhóm.

## Một quyết định tôi có thể tự giải thích

Quyết định đáng nói nhất: khi cho `chatbot.py` đọc chunk trực tiếp từ cache thay vì
luôn re-chunk tài liệu gốc, tôi **không** cho nó tin cache một cách vô điều kiện. Trước
khi dùng cache làm nguồn truy hồi, code so sánh tập `chunk_id` sống (chunk hiện tại từ
`load_documents()` + `chunks_from_documents()`) với tập `chunk_id` có trong cache — chỉ
dùng cache khi nó là **superset** đầy đủ của tập chunk sống. Nếu thiếu (ví dụ quên chạy
`precompute_embeddings.py` sau khi sửa data), hệ thống tự động rơi về hành vi cũ
(re-chunk trực tiếp từ tài liệu gốc) thay vì âm thầm trả lời dựa trên dữ liệu
thiếu/cũ. Đánh đổi là mỗi lần chạy vẫn phải tốn một lần re-chunk (rẻ, chỉ regex) để
kiểm tra, nhưng đổi lại tránh được lỗi khó phát hiện — độ chính xác quan trọng hơn một
chút tốc độ ở đây vì đây là phần quyết định chatbot có bịa hay không.

## AI đã hỗ trợ tôi như thế nào

Tôi dùng Claude Code để hiện thực cả hai thay đổi trên, chạy thử và đọc log trước khi
tin kết quả (không chỉ tin lời AI nói "đã xong"). Cụ thể AI đã giúp phát hiện một lỗi
thật trong lúc test (xem mục case fail bên dưới) trước khi nó lọt vào code — nếu không
kiểm tra kỹ ở bước đó, chatbot có thể đã trả lời dựa trên một phần rất nhỏ của kho dữ
liệu mà không ai biết. AI cũng giúp tôi tính lại chi phí trước khi chạy lại
`precompute_embeddings.py` (script gọi API OpenAI thật, tốn phí) thay vì chạy bừa.

## Case fail của nhóm và điều tôi học được

Lúc mới thêm logic "dùng cache nếu có, nếu không thì fallback", điều kiện fallback ban
đầu chỉ kiểm tra `if not chunks` (cache rỗng thì mới fallback). Khi test bằng dữ liệu
thật, cache lúc đó đang ở trạng thái migrate dở dang — có 240 entry nhưng chỉ 10 cái có
field `text` mới. Vì 10 vẫn là "không rỗng", điều kiện `if not chunks` không bắt được
trường hợp này: nếu không sửa, chatbot sẽ âm thầm trả lời dựa trên 10/240 đoạn tài liệu
thay vì toàn bộ, mà không có cảnh báo gì. Bài học: kiểm tra "có dữ liệu hay không" là
chưa đủ khi dữ liệu có thể **có một phần** — phải so sánh với tập đầy đủ mong đợi
(ở đây là so `chunk_id` với tài liệu gốc) thì mới bắt được lỗi dạng "thiếu một phần".

## Nếu làm lại, tôi sẽ thay đổi gì

- Viết test nhỏ cho `chunk_text()` (độ dài min/max, overlap đúng ký tự) trước khi đổi
  thuật toán, thay vì chỉ test tay bằng cách in ra và đọc số liệu.
- Golden set (`eval/golden_cases.json`) hiện chỉ có 5 case và `run_eval.py` chưa tự
  chấm đúng/sai — nếu làm lại tôi sẽ ưu tiên viết phần chấm điểm tự động sớm hơn, để
  mỗi lần đổi retrieval/chunk có con số so sánh trước/sau thay vì chỉ đọc code bằng mắt.
- Ghi rõ quy ước "sửa data trong `data/vlearn-pack/` thì phải chạy lại
  `precompute_embeddings.py`" thành một bước checklist hoặc script kiểm tra, vì đây là
  điều dễ quên và cache đang là nguồn dữ liệu chính cho retrieval.
