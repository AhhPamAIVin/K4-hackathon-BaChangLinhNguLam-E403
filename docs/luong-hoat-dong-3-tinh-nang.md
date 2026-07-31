# Luồng hoạt động 3 tính năng AI của VLearn

## Tổng quan

```mermaid
flowchart LR
    U[Người học] --> FE[Frontend React]
    FE --> QA[Tool hỏi đáp kiến thức]
    FE --> SR[Tool ôn tập và ghi nhớ]
    FE --> QZ[Tool tạo trắc nghiệm]

    QA --> RAG[(Chunk + Embedding index)]
    SR --> RAG
    QZ --> SUM[(Structured summaries)]

    RAG --> LLM[OpenAI Responses API]
    SUM --> LLM
    LLM --> FE
```

Backend chỉ sử dụng hai loại dữ liệu đã xử lý:

- `backend/data/processed/embeddings`: retrieval cho hỏi đáp và ôn tập.
- `backend/data/processed/summaries`: nguồn có cấu trúc để tạo quiz.

Mọi request đi qua guardrail cục bộ trước khi gọi embedding hoặc model. Các
nhóm bị chặn gồm: ngoài phạm vi học tập, prompt injection/đánh cắp prompt, xâm
phạm dữ liệu cá nhân và hướng dẫn nguy hiểm.

```mermaid
flowchart LR
    R[Request người học] --> G{Learning guardrail}
    G -->|Học tập hợp lệ| AI[Retrieval / Summary / Model]
    G -->|Ngoài phạm vi| S[Trả lời giới hạn phạm vi]
    G -->|Prompt injection| P[Từ chối đổi hoặc tiết lộ quy tắc]
    G -->|Privacy| D[Từ chối suy đoán danh tính]
    G -->|Unsafe| U[Từ chối hướng dẫn gây hại]
```

## 1. Hỏi đáp kiến thức trong lúc đọc

Người học có hai cách mở cùng một panel hỏi đáp:

1. Bấm nút AI nổi để hỏi kiến thức bình thường.
2. Bôi đen nội dung slide, bấm **Hỏi VLearn AI Agent** và hỏi về đoạn đã chọn.

```mermaid
sequenceDiagram
    actor User as Người học
    participant Slide as Slide Reader
    participant Panel as AI Tutor Panel
    participant API as POST /direct-qa/chat
    participant Retrieval as Hybrid Retrieval
    participant Model as gpt-5.6-luna

    User->>Slide: Bôi đen nội dung PDF
    Slide-->>User: Hiện tooltip Hỏi AI
    User->>Slide: Bấm Hỏi VLearn AI Agent
    Slide->>Panel: Mở panel + text + source + page
    User->>Panel: Nhập câu hỏi
    Panel->>API: message + history + selection
    API->>Retrieval: Embed câu hỏi và tìm top chunks
    Retrieval-->>API: Context + citation hợp lệ
    API->>Model: Câu hỏi + context + selection
    Model-->>API: Answer + citation + câu hỏi gợi ý
    API-->>Panel: AgentAnswer
    Panel-->>User: Hiển thị trả lời và citation
```

Selection từ PDF chỉ được chấp nhận khi:

- `source` là tên một slide có thật trong data backend.
- Có `page` hợp lệ.
- Selection chỉ làm context bổ sung, không được dùng làm citation.

## 2. Hỏi đáp ôn tập và ghi nhớ

Tab **Ôn tập** có phạm vi Ngày 1/Ngày 2 và các lối vào gợi ý như tự kiểm
tra, so sánh khái niệm và tạo mẹo nhớ. Tool này dùng cùng knowledge index với
hỏi đáp thường nhưng có prompt sư phạm khác.

```mermaid
flowchart TD
    A[Chọn ngày học] --> B[Chọn gợi ý hoặc nhập nội dung muốn ôn]
    B --> C[POST /api/v1/agents/study/review]
    C --> D[Semantic retrieval có lọc theo day]
    D --> E[Context transcript + citations]
    E --> F[Study Review Tool]
    F --> G{Mục tiêu câu hỏi}
    G -->|Nhớ lại| H[Câu hỏi gợi mở]
    G -->|Hiểu sai| I[Chỉ rõ điểm sai và sửa]
    G -->|Ghi nhớ| J[So sánh hoặc mẹo nhớ]
    H --> K[Trả lời trong panel]
    I --> K
    J --> K
```

Lịch sử hội thoại được gửi tối đa 12 message gần nhất từ frontend; backend
giới hạn tối đa 20 message.

## 3. Trắc nghiệm kiểm tra hiểu bài

Người học cấu hình ngày học, số câu và độ khó ngay trong tab **Trắc nghiệm**.
Quiz được tạo từ summary có cấu trúc, không lấy trực tiếp từ đoạn retrieval.

```mermaid
sequenceDiagram
    actor User as Người học
    participant Panel as Quiz Panel
    participant API as POST /study/quiz
    participant Summary as Summary index
    participant Model as gpt-5.6-luna

    User->>Panel: Chọn ngày, số câu, độ khó
    Panel->>API: Yêu cầu tự nhiên
    API->>Summary: Nạp summary đúng ngày
    Summary-->>API: Concepts, examples, misconceptions, citations
    API->>Model: Structured summary + JSON schema
    Model-->>API: Quiz JSON
    API->>API: Kiểm tra 4 đáp án, đáp án đúng và citation
    API-->>Panel: QuizResponse
    loop Từng câu
        User->>Panel: Chọn đáp án
        Panel-->>User: Đúng/sai + giải thích + citation
    end
```

## Trạng thái lỗi chung

```mermaid
flowchart LR
    A[Frontend gửi request] --> B{Backend phản hồi}
    B -->|2xx| C[Hiển thị kết quả]
    B -->|4xx| D[Hiển thị lỗi dữ liệu/yêu cầu]
    B -->|503| E[Thông báo model hoặc API key chưa sẵn sàng]
    A -->|Timeout 90 giây| F[Cho phép người học thử lại]
    A -->|Không kết nối| G[Nhắc chạy backend cổng 8000]
```

## File triển khai chính

- `frontend/src/components/SlideReaderView.jsx`: đọc PDF và bắt selection.
- `frontend/src/components/AiTutorPanel.jsx`: ba giao diện AI.
- `frontend/src/services/vlearnApi.js`: giao tiếp với FastAPI.
- `backend/app/tools/knowledge_qa.py`: hỏi đáp kiến thức.
- `backend/app/tools/study_review.py`: ôn tập và ghi nhớ.
- `backend/app/tools/generate_quiz.py`: tạo trắc nghiệm.
