"""Guardrail cục bộ cho phạm vi học tập và an toàn đầu vào."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Literal


GuardrailCode = Literal[
    "scope",
    "prompt_injection",
    "privacy",
    "unsafe",
    "ambiguous",
]


@dataclass(frozen=True)
class GuardrailDecision:
    allowed: bool
    code: GuardrailCode | None = None
    message: str | None = None


def normalize_for_matching(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.casefold())
    without_accents = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )
    without_accents = without_accents.replace("đ", "d")
    return re.sub(r"\s+", " ", without_accents).strip()


PROMPT_INJECTION_PATTERNS = (
    r"\bbo qua (?:tat ca |cac )?(?:huong dan|quy tac|prompt)\b",
    r"\bignore (?:all |the )?(?:previous|prior|system) instructions?\b",
    r"\b(?:tiet lo|hien thi|in ra|show|reveal) (?:system |developer )?prompt\b",
    r"\b(?:system|developer) (?:message|instructions?)\b",
    r"\bjailbreak\b",
    r"\bdan\b.*\bmode\b",
    r"\bapi key\b",
    r"\bchuoi bi mat\b",
)

PRIVACY_PATTERNS = (
    r"\b(?:giai|pha|truy tim) an danh\b",
    r"\b(?:doan|tim|xet) danh tinh\b",
    r"\bthong tin ca nhan (?:hoc vien|giang vien)\b",
    r"\bten that cua (?:hoc vien|nguoi hoc)\b",
    r"\bre-?identify\b",
)

UNSAFE_PATTERNS = (
    r"\b(?:cach|huong dan) (?:lam|che tao) (?:bom|vu khi|chat no)\b",
    r"\b(?:viet|tao|phat tan) (?:malware|ransomware|virus may tinh)\b",
    r"\bhack (?:tai khoan|mat khau|he thong)\b",
    r"\b(?:lua dao|phishing) (?:nguoi|tai khoan|ngan hang)\b",
    r"\b(?:cach|huong dan) (?:tu tu|tu hai|lam hai nguoi)\b",
)

OFF_TOPIC_PATTERNS = (
    r"\b(?:du bao )?thoi tiet\b",
    r"\b(?:ti so|ket qua) (?:bong da|the thao)\b",
    r"\b(?:gia|mua|ban) (?:vang|bitcoin|co phieu)\b",
    r"\btu van dau tu\b",
    r"\b(?:hen ho|tan tinh)\b",
    r"\b(?:cong thuc|cach) nau (?:an|mon)\b",
    r"\b(?:dat ve|lich trinh) du lich\b",
    r"\b(?:bau cu|ung cu vien|chinh tri)\b",
    r"\b(?:viet|sang tac) (?:tho|nhac|truyen)\b",
    r"\b(?:xem boi|tu vi|cung hoang dao)\b",
    r"\b(?:phim|bai hat|tro choi) nao hay\b",
    r"\b(?:chan doan|ke don|tu van) (?:benh|thuoc|y te)\b",
    r"\btu van (?:phap ly|kien tung)\b",
    r"\bdat (?:giup )?(?:toi|minh )?(?:mot )?lich hen\b",
)

GREETING_ONLY_RE = re.compile(
    r"^(?:xin chao|chao|hello|hi|hey|cam on|thank you|thanks)[!. ]*$"
)

AMBIGUOUS_PATTERNS = (
    r"^cai nay la gi[?.! ]*$",
    r"^giai thich (?:them|ro hon)(?: di)?[?.! ]*$",
    r"^(?:y|doan) nay la sao[?.! ]*$",
    r"^no khac gi[?.! ]*$",
    r"^tai sao (?:lai )?vay[?.! ]*$",
    r"^cho (?:minh|toi) vi du(?: di)?[?.! ]*$",
    r"^tom tat(?: di)?[?.! ]*$",
    r"^giup (?:minh|toi) voi[?.! ]*$",
)


def _matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def evaluate_learning_request(
    text: str,
    *,
    has_learning_context: bool = False,
) -> GuardrailDecision:
    normalized = normalize_for_matching(text)

    if _matches_any(normalized, PROMPT_INJECTION_PATTERNS):
        return GuardrailDecision(
            allowed=False,
            code="prompt_injection",
            message=(
                "Mình không thể thay đổi hoặc tiết lộ quy tắc hệ thống. "
                "Bạn có thể tiếp tục hỏi về kiến thức trong học liệu VLearn."
            ),
        )
    if _matches_any(normalized, PRIVACY_PATTERNS):
        return GuardrailDecision(
            allowed=False,
            code="privacy",
            message=(
                "Mình không hỗ trợ suy đoán danh tính hay khai thác thông tin "
                "cá nhân. Hãy hỏi về nội dung học tập đã được ẩn danh."
            ),
        )
    if _matches_any(normalized, UNSAFE_PATTERNS):
        return GuardrailDecision(
            allowed=False,
            code="unsafe",
            message=(
                "Mình không thể hỗ trợ hướng dẫn có thể gây hại. "
                "Mình có thể giúp bạn học và ôn tập nội dung an toàn trong khóa."
            ),
        )
    if _matches_any(normalized, OFF_TOPIC_PATTERNS) or (
        not has_learning_context and GREETING_ONLY_RE.fullmatch(normalized)
    ):
        return GuardrailDecision(
            allowed=False,
            code="scope",
            message=(
                "Mình chỉ hỗ trợ câu hỏi học tập dựa trên học liệu VLearn. "
                "Bạn hãy hỏi về một khái niệm, bài giảng hoặc nội dung cần ôn."
            ),
        )
    if not has_learning_context and _matches_any(
        normalized,
        AMBIGUOUS_PATTERNS,
    ):
        return GuardrailDecision(
            allowed=False,
            code="ambiguous",
            message=(
                "Mình cần thêm ngữ cảnh để trả lời chính xác. Bạn hãy nêu tên "
                "khái niệm, ngày học hoặc bôi đen đoạn slide muốn hỏi."
            ),
        )
    return GuardrailDecision(allowed=True)
