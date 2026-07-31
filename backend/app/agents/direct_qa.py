"""Compatibility import; implementation đã chuyển sang tools."""

from backend.app.tools.knowledge_qa import KnowledgeQATool

DirectQAAgent = KnowledgeQATool

__all__ = ["DirectQAAgent"]
