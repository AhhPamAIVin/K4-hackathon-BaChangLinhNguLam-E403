# VLearn AI Backend

FastAPI backend gồm ba năng lực:

1. `knowledge_qa`: hỏi đáp kiến thức thông thường từ transcript.
2. `study_review`: hỏi đáp theo hướng ôn tập, chủ động nhớ lại và ghi nhớ.
3. `generate_quiz`: tạo câu hỏi trắc nghiệm từ summary có cấu trúc.

## Cấu trúc

```text
backend/
├── app/
│   ├── data_processing/
│   │   ├── summarize.py          # transcript -> summary cho quiz
│   │   ├── chunking.py           # chunk ~700 ký tự, overlap ~100
│   │   └── build_embeddings.py   # metadata + OpenAI embeddings
│   ├── tools/
│   │   ├── knowledge_qa.py
│   │   ├── study_review.py
│   │   └── generate_quiz.py
│   ├── api/
│   ├── core/
│   ├── models/
│   └── services/
├── data/
│   ├── raw/vlearn-pack/
│   └── processed/
│       ├── summaries/
│       └── embeddings/
└── tests/
```

Summary và embedding là hai pipeline độc lập:

- Summary giữ các learning objective, concept, ví dụ, so sánh, misconception
  và citation để model tạo trắc nghiệm có căn cứ.
- Embedding index giữ text chunk cùng `source`, `day`, `chunk_index`,
  vị trí ký tự, citation IDs và content hash để phục vụ retrieval cho cả hai
  tool hỏi đáp.

## Cài đặt

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
Copy-Item backend/.env.example .env
```

Điền `OPENAI_API_KEY` trong `.env`.

## Xử lý dữ liệu

Kiểm tra/tạo summary:

```powershell
python -m backend.app.data_processing.summarize --check
python -m backend.app.data_processing.summarize
```

Tạo chunk + metadata mà chưa gọi API:

```powershell
python -m backend.app.data_processing.build_embeddings --chunks-only
```

Tạo cả chunk và vector:

```powershell
python -m backend.app.data_processing.build_embeddings
```

Mặc định dùng chunk 700 ký tự, overlap 100 ký tự. Có thể tune bằng
`--target-chars` và `--overlap-chars`.

## Model mặc định

- Sinh câu trả lời, summary và quiz: `gpt-5.6-luna`, reasoning `low`.
- Embedding: `text-embedding-3-small`, 1024 chiều.

Đây là cấu hình ưu tiên tốc độ/chi phí cho workload học liệu khối lượng lớn.
Có thể đổi riêng từng tác vụ qua `OPENAI_BACKEND_MODEL`,
`OPENAI_SUMMARY_MODEL`, `OPENAI_QUIZ_MODEL`, `OPENAI_EMBEDDING_MODEL`,
`OPENAI_EMBEDDING_DIMENSIONS` và `OPENAI_REASONING_EFFORT`.

## Chạy và test

```powershell
uvicorn backend.app.main:app --reload
pytest backend/tests -q
```

- API docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## API

- `POST /api/v1/agents/direct-qa/chat`
- `POST /api/v1/agents/study/review`
- `POST /api/v1/agents/study/quiz`
