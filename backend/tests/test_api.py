from fastapi.testclient import TestClient

from backend.app.dependencies import get_direct_qa_agent, get_study_agent
from backend.app.main import app
from backend.app.models.api import (
    AgentAnswer,
    Citation,
    QuizResponse,
)


class FakeDirectAgent:
    def answer(self, request):
        return AgentAnswer(
            agent="direct_qa",
            answer=f"Trả lời cho: {request.message}",
            citations=[Citation(id="[T04-001]", source="transcript-04-clean.md")],
            suggested_questions=["Câu hỏi tiếp theo?"],
        )


class FakeStudyAgent:
    def create_quiz(self, request):
        return QuizResponse.model_validate(
            {
                "quiz_title": "Quiz Day 1",
                "questions": [
                    {
                        "id": "q01",
                        "type": "single_choice",
                        "question": "Câu hỏi thử?",
                        "options": [
                            {"id": "A", "text": "A"},
                            {"id": "B", "text": "B"},
                            {"id": "C", "text": "C"},
                            {"id": "D", "text": "D"},
                        ],
                        "correct_option_id": "A",
                        "explanation": "Giải thích.",
                        "citations": ["[T04-001]"],
                        "difficulty": "easy",
                        "learning_objective": "Kiểm tra kiến thức.",
                    }
                ],
                "metadata": {
                    "question_count": 1,
                    "source_summaries": ["transcript-04-clean.md"],
                    "model": "fake-model",
                },
            }
        )

    def review(self, request):
        return AgentAnswer(
            agent="study",
            answer=f"Ôn tập: {request.message}",
            citations=[Citation(id="[T02-001]", source="transcript-02-clean.md")],
            suggested_questions=[],
        )


app.dependency_overrides[get_direct_qa_agent] = lambda: FakeDirectAgent()
app.dependency_overrides[get_study_agent] = lambda: FakeStudyAgent()
client = TestClient(app)


def test_health_reports_loaded_knowledge() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["transcript_count"] == 6
    assert response.json()["summary_count"] == 6


def test_direct_chat_contract() -> None:
    response = client.post(
        "/api/v1/agents/direct-qa/chat",
        json={"message": "Attention là gì?", "history": []},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["agent"] == "direct_qa"
    assert payload["citations"][0]["id"] == "[T04-001]"


def test_quiz_contract() -> None:
    response = client.post(
        "/api/v1/agents/study/quiz",
        json={"request": "Tạo một câu ngày 1"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["questions"][0]["correct_option_id"] == "A"
    assert len(payload["questions"][0]["options"]) == 4


def test_study_review_contract() -> None:
    response = client.post(
        "/api/v1/agents/study/review",
        json={
            "message": "Ôn lại augment và automate",
            "day": "day-2",
            "history": [],
        },
    )
    assert response.status_code == 200
    assert response.json()["agent"] == "study"


def test_rejects_invalid_day() -> None:
    response = client.post(
        "/api/v1/agents/study/review",
        json={"message": "Ôn tập", "day": "day-3"},
    )
    assert response.status_code == 422
