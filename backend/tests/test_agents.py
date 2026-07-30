from pathlib import Path

from backend.app.agents.direct_qa import DirectQAAgent
from backend.app.agents.study import StudyAgent
from backend.app.models.api import DirectChatRequest, StudyChatRequest
from backend.app.services.knowledge_base import (
    SummaryKnowledgeBase,
    TranscriptKnowledgeBase,
)


ROOT = Path(__file__).resolve().parents[2]


class FakeOpenAIService:
    def generate_answer(self, *, instructions: str, user_input: str) -> dict:
        if "agent hỏi đáp trực tiếp" in instructions:
            return {
                "answer": "Attention giúp mô hình tập trung vào phần liên quan.",
                "citations": ["[T06-075]", "[T99-999]"],
                "suggested_questions": ["Self-attention là gì?"],
            }
        return {
            "answer": "Augment hỗ trợ con người, automate tự động hoá công việc.",
            "citations": ["[T02-001]", "[T99-999]"],
            "suggested_questions": [],
        }


def test_transcript_knowledge_base_has_all_segments() -> None:
    knowledge = TranscriptKnowledgeBase(
        ROOT / "data" / "vlearn-pack" / "transcript"
    )
    assert len(knowledge.documents) == 6
    assert len(knowledge.records) == 700


def test_direct_agent_filters_hallucinated_citation() -> None:
    knowledge = TranscriptKnowledgeBase(
        ROOT / "data" / "vlearn-pack" / "transcript"
    )
    agent = DirectQAAgent(knowledge, FakeOpenAIService())
    response = agent.answer(DirectChatRequest(message="Attention hoạt động thế nào?"))
    assert [citation.id for citation in response.citations] == ["[T06-075]"]


def test_study_knowledge_base_loads_v2_summaries() -> None:
    output = ROOT / "feature" / "question" / "output"
    knowledge = SummaryKnowledgeBase(
        output / "summary-index.json",
        output / "summaries",
    )
    assert len(knowledge.summaries) == 6
    assert len(knowledge.records) > 300


def test_study_agent_filters_hallucinated_citation() -> None:
    output = ROOT / "feature" / "question" / "output"
    knowledge = SummaryKnowledgeBase(
        output / "summary-index.json",
        output / "summaries",
    )
    agent = StudyAgent(knowledge, FakeOpenAIService())
    response = agent.review(
        StudyChatRequest(
            message="Augment và automate khác nhau thế nào?",
            day="day-2",
        )
    )
    assert all(citation.id != "[T99-999]" for citation in response.citations)
