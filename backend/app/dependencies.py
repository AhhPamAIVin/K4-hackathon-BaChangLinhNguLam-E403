from functools import lru_cache

from backend.app.agents.direct_qa import DirectQAAgent
from backend.app.agents.study import StudyAgent
from backend.app.core.config import Settings
from backend.app.services.knowledge_base import (
    SummaryKnowledgeBase,
    TranscriptKnowledgeBase,
)
from backend.app.services.openai_service import OpenAIService


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()


@lru_cache
def get_transcript_knowledge_base() -> TranscriptKnowledgeBase:
    return TranscriptKnowledgeBase(get_settings().transcript_dir)


@lru_cache
def get_summary_knowledge_base() -> SummaryKnowledgeBase:
    settings = get_settings()
    return SummaryKnowledgeBase(settings.summary_index, settings.summary_dir)


@lru_cache
def get_openai_service() -> OpenAIService:
    return OpenAIService(get_settings())


def get_direct_qa_agent() -> DirectQAAgent:
    return DirectQAAgent(get_transcript_knowledge_base(), get_openai_service())


def get_study_agent() -> StudyAgent:
    return StudyAgent(get_summary_knowledge_base(), get_openai_service())
