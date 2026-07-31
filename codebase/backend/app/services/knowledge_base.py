import json
import math
import re
from dataclasses import dataclass
from pathlib import Path


SEGMENT_RE = re.compile(
    r"\*\*(\[T\d{2}-\d{3}\])\*\*\s*(.*?)"
    r"(?=\n\s*\*\*\[T\d{2}-\d{3}\]\*\*|\Z)",
    re.DOTALL,
)
TOKEN_RE = re.compile(r"[a-z0-9\u00c0-\u024f]+", re.IGNORECASE)
DAY_BY_SOURCE = {
    "transcript-04-clean.md": "day-1",
    "transcript-06-clean.md": "day-1",
    "transcript-01-clean.md": "day-2",
    "transcript-02-clean.md": "day-2",
    "transcript-03-clean.md": "day-2",
    "transcript-05-clean.md": "day-2",
}


def tokenize(text: str) -> set[str]:
    return {token.casefold() for token in TOKEN_RE.findall(text)}


def rank(query: str, records: list[dict], top_k: int) -> list[dict]:
    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    scored: list[tuple[float, dict]] = []
    normalized_query = " ".join(query.casefold().split())
    for record in records:
        text = record["text"]
        text_tokens = tokenize(text)
        overlap = len(query_tokens & text_tokens)
        if overlap == 0:
            continue
        coverage = overlap / len(query_tokens)
        phrase_bonus = 1.0 if normalized_query in text.casefold() else 0.0
        scored.append((coverage + overlap * 0.05 + phrase_bonus, record))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [record for _, record in scored[:top_k]]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


def load_jsonl(path: Path | None) -> list[dict]:
    if path is None or not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


@dataclass
class TranscriptKnowledgeBase:
    transcript_dir: Path
    chunk_index: Path | None = None
    vector_index: Path | None = None

    def __post_init__(self) -> None:
        self.records: list[dict] = []
        self.documents: dict[str, str] = {}
        slides_dir = self.transcript_dir.parent / "slides"
        self.slide_sources = {
            path.name for path in slides_dir.glob("*.pdf") if path.is_file()
        }
        for path in sorted(self.transcript_dir.glob("transcript-*-clean.md")):
            content = path.read_text(encoding="utf-8")
            self.documents[path.name] = content
            for citation, text in SEGMENT_RE.findall(content):
                cleaned = " ".join(text.split())
                if cleaned:
                    self.records.append(
                        {
                            "citation": citation,
                            "citations": [citation],
                            "source": path.name,
                            "day": DAY_BY_SOURCE.get(path.name),
                            "text": cleaned,
                        }
                    )
        chunks = load_jsonl(self.chunk_index)
        vectors = {
            record["id"]: record["embedding"]
            for record in load_jsonl(self.vector_index)
            if isinstance(record.get("embedding"), list)
        }
        if chunks:
            self.records = [
                {
                    "id": chunk["id"],
                    "citation": (
                        chunk["metadata"].get("citation_ids") or ["unknown"]
                    )[0],
                    "citations": chunk["metadata"].get("citation_ids", []),
                    "source": chunk["metadata"]["source"],
                    "day": chunk["metadata"].get("day"),
                    "text": chunk["text"],
                    "embedding": vectors.get(chunk["id"]),
                    "metadata": chunk["metadata"],
                }
                for chunk in chunks
            ]
        self.vector_count = sum(
            1 for record in self.records if record.get("embedding")
        )
        self.has_embeddings = self.vector_count > 0
        self.embedding_ready = (
            bool(self.records) and self.vector_count == len(self.records)
        )

    def search(
        self,
        query: str,
        top_k: int = 6,
        query_embedding: list[float] | None = None,
        day: str | None = None,
    ) -> list[dict]:
        candidates = [
            record
            for record in self.records
            if day is None or record.get("day") == day
        ]
        if query_embedding and self.has_embeddings:
            query_tokens = tokenize(query)
            scored: list[tuple[float, dict]] = []
            for record in candidates:
                embedding = record.get("embedding")
                if not embedding:
                    continue
                semantic = cosine_similarity(query_embedding, embedding)
                lexical = len(query_tokens & tokenize(record["text"])) / max(
                    len(query_tokens),
                    1,
                )
                scored.append((semantic * 0.8 + lexical * 0.2, record))
            scored.sort(key=lambda item: item[0], reverse=True)
            return [record for _, record in scored[:top_k]]
        return rank(query, candidates, top_k)

    def validate_selection(
        self,
        text: str,
        source: str,
        page: int | None = None,
    ) -> bool:
        document = self.documents.get(source)
        normalized_text = " ".join(text.casefold().split())
        if not normalized_text:
            return False
        if document:
            normalized_document = " ".join(document.casefold().split())
            return normalized_text in normalized_document
        # PDF selection đến từ text layer của đúng slide nội bộ. Không dùng
        # selection này làm citation; nó chỉ là context bổ sung cho câu hỏi.
        return source in self.slide_sources and page is not None


@dataclass
class SummaryKnowledgeBase:
    index_path: Path
    summary_dir: Path

    def __post_init__(self) -> None:
        self.summaries: list[dict] = []
        self.records: list[dict] = []
        if not self.index_path.is_file():
            return
        index = json.loads(self.index_path.read_text(encoding="utf-8"))
        output_dir = self.index_path.parent
        for day, entries in index.get("days", {}).items():
            for entry in entries:
                path = output_dir / entry["summary_file"]
                if not path.is_file():
                    continue
                summary = json.loads(path.read_text(encoding="utf-8"))
                if summary.get("metadata", {}).get("schema_version") != 2:
                    continue
                summary["_day"] = day
                self.summaries.append(summary)
                self._add_summary_records(summary, entry["source_transcript"], day)

    def _add_summary_records(self, summary: dict, source: str, day: str) -> None:
        for objective in summary.get("learning_objectives", []):
            self.records.append(
                {
                    "text": objective,
                    "citations": [],
                    "source": source,
                    "day": day,
                }
            )
        for group in (
            "key_concepts",
            "testable_points",
            "examples",
            "comparisons",
            "misconceptions",
        ):
            for item in summary.get(group, []):
                text = " ".join(
                    value
                    for key, value in item.items()
                    if key != "citations" and isinstance(value, str)
                )
                self.records.append(
                    {
                        "text": text,
                        "citations": item.get("citations", []),
                        "source": source,
                        "day": day,
                    }
                )

    def search(self, query: str, day: str | None, top_k: int = 8) -> list[dict]:
        records = [
            record for record in self.records if day is None or record["day"] == day
        ]
        results = rank(query, records, top_k)
        if results:
            return results
        return [record for record in records if record["citations"]][:top_k]
