# VLearn AI Backend

FastAPI backend gồm hai agent:

1. `direct_qa`: hỏi đáp trực tiếp dựa trên transcript gốc.
2. `study`: tạo quiz từ summary schema v2 và hỏi đáp ôn tập.

## Chuẩn bị

Từ thư mục gốc:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
Copy-Item backend/.env.example .env
```

Điền `OPENAI_API_KEY`. Trước khi dùng study agent:

```powershell
python feature/question/process_data.py
```

## Chạy

```powershell
uvicorn backend.app.main:app --reload
```

- API docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## Test

Test dùng fake agent, không gọi OpenAI:

```powershell
pip install -r backend/requirements-dev.txt
pytest backend/tests -q
```

## API

### Hỏi đáp trực tiếp

`POST /api/v1/agents/direct-qa/chat`

```json
{
  "message": "Attention hoạt động như thế nào?",
  "history": []
}
```

Có thể truyền thêm đoạn người học bôi đen:

```json
{
  "message": "Giải thích đoạn này dễ hiểu hơn",
  "history": [],
  "selection": {
    "text": "Nội dung có thật trong transcript...",
    "source": "transcript-04-clean.md",
    "page": null
  }
}
```

### Tạo quiz

`POST /api/v1/agents/study/quiz`

```json
{
  "request": "Tạo 5 câu ngày 1, mức độ từ dễ đến khó"
}
```

### Hỏi đáp ôn tập

`POST /api/v1/agents/study/review`

```json
{
  "message": "So sánh augment và automate để mình ôn lại",
  "day": "day-2",
  "history": []
}
```

## Cấu trúc

```text
backend/
├── app/
│   ├── agents/       # logic hai agent
│   ├── api/          # FastAPI routes
│   ├── core/         # settings
│   ├── models/       # request/response schemas
│   ├── services/     # knowledge base và OpenAI
│   ├── dependencies.py
│   └── main.py
├── tests/
└── requirements.txt
```
