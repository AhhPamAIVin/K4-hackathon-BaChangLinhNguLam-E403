import json
import os

from backend.app.core.config import Settings


ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "citations": {
            "type": "array",
            "items": {"type": "string"},
        },
        "suggested_questions": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 3,
        },
    },
    "required": ["answer", "citations", "suggested_questions"],
    "additionalProperties": False,
}


class OpenAIService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate_answer(self, *, instructions: str, user_input: str) -> dict:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("Thiếu OPENAI_API_KEY.")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Chưa cài package openai.") from exc

        response = OpenAI().responses.create(
            model=self.settings.openai_model,
            reasoning={"effort": self.settings.reasoning_effort},
            instructions=instructions,
            input=user_input,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "agent_answer",
                    "strict": True,
                    "schema": ANSWER_SCHEMA,
                }
            },
        )
        if not response.output_text:
            raise RuntimeError("OpenAI không trả về nội dung.")
        try:
            payload = json.loads(response.output_text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("OpenAI trả về JSON không hợp lệ.") from exc
        return payload
