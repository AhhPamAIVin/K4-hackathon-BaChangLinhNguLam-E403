# VLearn Prototype

Thư mục này chứa toàn bộ mã nguồn chạy của prototype:

```text
codebase/
├── frontend/   # React + Vite, trình đọc slide và AI Tutor panel
└── backend/    # FastAPI, RAG, guardrail, quiz và pipeline dữ liệu
```

Chạy backend từ thư mục gốc:

```powershell
.\.venv\Scripts\Activate.ps1
Set-Location codebase
uvicorn backend.app.main:app --reload
```

Chạy frontend trong terminal khác:

```powershell
Set-Location codebase/frontend
npm install
npm run dev
```

Chi tiết backend nằm tại `codebase/backend/README.md`.
