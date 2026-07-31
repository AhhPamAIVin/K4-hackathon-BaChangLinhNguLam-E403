"""Compatibility adapter cho API cũ."""

from backend.app.models.api import QuizRequest, QuizResponse
from backend.app.tools.generate_quiz import generate_quiz
from backend.app.tools.study_review import StudyReviewTool
from backend.app.services.guardrails import evaluate_learning_request


class StudyAgent(StudyReviewTool):
    def create_quiz(self, request: QuizRequest) -> QuizResponse:
        guardrail = evaluate_learning_request(request.request)
        if not guardrail.allowed:
            raise ValueError(guardrail.message)
        return QuizResponse.model_validate_json(generate_quiz(request.request))


__all__ = ["StudyAgent"]
