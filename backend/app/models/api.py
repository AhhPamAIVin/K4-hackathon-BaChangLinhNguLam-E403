from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ChatMessage(ApiModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=8000)


class TextSelection(ApiModel):
    text: str = Field(min_length=1, max_length=12000)
    source: str = Field(min_length=1, max_length=255)
    page: int | None = Field(default=None, ge=1)


class DirectChatRequest(ApiModel):
    message: str = Field(min_length=2, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)
    selection: TextSelection | None = None


class StudyChatRequest(ApiModel):
    message: str = Field(min_length=2, max_length=4000)
    day: Literal["day-1", "day-2"] | None = None
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class Citation(ApiModel):
    id: str
    source: str


class AgentAnswer(ApiModel):
    agent: Literal["direct_qa", "study"]
    answer: str
    citations: list[Citation]
    suggested_questions: list[str]
    blocked: bool = False
    guardrail_code: Literal[
        "scope",
        "prompt_injection",
        "privacy",
        "unsafe",
        "ambiguous",
    ] | None = None
    needs_clarification: bool = False


class QuizRequest(ApiModel):
    request: str = Field(
        min_length=2,
        max_length=2000,
        examples=["Tạo 5 câu ngày 1, mức độ từ dễ đến khó"],
    )


class QuizOption(ApiModel):
    id: Literal["A", "B", "C", "D"]
    text: str


class QuizQuestion(ApiModel):
    id: str
    type: Literal["single_choice"]
    question: str
    options: list[QuizOption] = Field(min_length=4, max_length=4)
    correct_option_id: Literal["A", "B", "C", "D"]
    explanation: str
    citations: list[str]
    difficulty: Literal["easy", "medium", "hard"]
    learning_objective: str


class QuizMetadata(ApiModel):
    question_count: int = Field(ge=1, le=20)
    source_summaries: list[str]
    model: str


class QuizResponse(ApiModel):
    quiz_title: str
    questions: list[QuizQuestion] = Field(min_length=1, max_length=20)
    metadata: QuizMetadata


class HealthResponse(ApiModel):
    status: Literal["ok"]
    transcript_count: int
    summary_count: int
    chunk_count: int
    vector_count: int
    embedding_ready: bool
