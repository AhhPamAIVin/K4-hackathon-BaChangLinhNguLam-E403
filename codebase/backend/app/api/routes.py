from fastapi import APIRouter, Depends, HTTPException

from backend.app.agents.direct_qa import DirectQAAgent
from backend.app.agents.study import StudyAgent
from backend.app.dependencies import (
    get_direct_qa_agent,
    get_study_agent,
    get_summary_knowledge_base,
    get_transcript_knowledge_base,
)
from backend.app.models.api import (
    AgentAnswer,
    DirectChatRequest,
    HealthResponse,
    QuizRequest,
    QuizResponse,
    StudyChatRequest,
)


router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    transcript_knowledge = get_transcript_knowledge_base()
    return HealthResponse(
        status="ok",
        transcript_count=len(transcript_knowledge.documents),
        summary_count=len(get_summary_knowledge_base().summaries),
        chunk_count=len(transcript_knowledge.records),
        vector_count=transcript_knowledge.vector_count,
        embedding_ready=transcript_knowledge.embedding_ready,
    )


@router.post(
    "/api/v1/agents/direct-qa/chat",
    response_model=AgentAnswer,
    tags=["direct-qa"],
)
def direct_chat(
    request: DirectChatRequest,
    agent: DirectQAAgent = Depends(get_direct_qa_agent),
) -> AgentAnswer:
    try:
        return agent.answer(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post(
    "/api/v1/agents/study/quiz",
    response_model=QuizResponse,
    tags=["study"],
)
def create_quiz(
    request: QuizRequest,
    agent: StudyAgent = Depends(get_study_agent),
) -> QuizResponse:
    try:
        return agent.create_quiz(request)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post(
    "/api/v1/agents/study/review",
    response_model=AgentAnswer,
    tags=["study"],
)
def study_review(
    request: StudyChatRequest,
    agent: StudyAgent = Depends(get_study_agent),
) -> AgentAnswer:
    try:
        return agent.review(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
