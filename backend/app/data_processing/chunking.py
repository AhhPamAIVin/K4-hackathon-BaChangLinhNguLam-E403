"""Tách transcript thành các chunk có độ dài ổn định và metadata truy vết."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


SEGMENT_RE = re.compile(
    r"\*\*(\[T\d{2}-\d{3}\])\*\*\s*(.*?)"
    r"(?=\n\s*\*\*\[T\d{2}-\d{3}\]\*\*|\Z)",
    re.DOTALL,
)


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def _cut_at_word(text: str, desired: int, lower_bound: int) -> int:
    if desired >= len(text):
        return len(text)
    sentence_candidates = [
        text.rfind(marker, lower_bound, desired)
        for marker in (". ", "? ", "! ", "; ")
    ]
    sentence_end = max(sentence_candidates)
    if sentence_end >= lower_bound:
        return sentence_end + 1
    word_end = text.rfind(" ", lower_bound, desired)
    return word_end if word_end >= lower_bound else desired


def chunk_transcript(
    path: Path,
    *,
    day: str,
    target_chars: int = 700,
    overlap_chars: int = 100,
) -> list[dict]:
    if target_chars < 200:
        raise ValueError("target_chars phải từ 200 trở lên.")
    if overlap_chars < 0 or overlap_chars >= target_chars:
        raise ValueError("overlap_chars phải >= 0 và nhỏ hơn target_chars.")

    raw = path.read_text(encoding="utf-8")
    parsed = [
        (citation, normalize_text(text))
        for citation, text in SEGMENT_RE.findall(raw)
        if normalize_text(text)
    ]
    if not parsed:
        raise ValueError(f"Không tìm thấy segment có citation trong {path}.")

    parts: list[str] = []
    spans: list[tuple[int, int, str]] = []
    cursor = 0
    for citation, text in parsed:
        if parts:
            cursor += 1
        start = cursor
        parts.append(text)
        cursor += len(text)
        spans.append((start, cursor, citation))
    document = " ".join(parts)

    chunks: list[dict] = []
    start = 0
    while start < len(document):
        desired_end = min(start + target_chars, len(document))
        end = _cut_at_word(
            document,
            desired_end,
            min(start + max(target_chars // 2, 1), desired_end),
        )
        text = document[start:end].strip()
        citations = [
            citation
            for segment_start, segment_end, citation in spans
            if segment_start < end and segment_end > start
        ]
        chunk_index = len(chunks)
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        chunks.append(
            {
                "id": f"{path.stem}:chunk-{chunk_index:04d}",
                "text": text,
                "metadata": {
                    "source": path.name,
                    "document_id": path.stem,
                    "day": day,
                    "chunk_index": chunk_index,
                    "char_start": start,
                    "char_end": end,
                    "char_count": len(text),
                    "citation_ids": citations,
                    "content_hash": content_hash,
                },
            }
        )
        if end >= len(document):
            break
        next_start = max(end - overlap_chars, start + 1)
        space = document.find(" ", next_start, min(end + 1, len(document)))
        start = space + 1 if space != -1 else next_start
    return chunks

