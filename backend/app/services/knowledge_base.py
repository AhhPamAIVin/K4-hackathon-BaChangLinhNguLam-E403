import json
import re
from dataclasses import dataclass
from pathlib import Path


SEGMENT_RE = re.compile(
    r"\*\*(\[T\d{2}-\d{3}\])\*\*\s*(.*?)"
    r"(?=\n\s*\*\*\[T\d{2}-\d{3}\]\*\*|\Z)",
    re.DOTALL,
)
TOKEN_RE = re.compile(r"[a-z0-9\u00c0-\u024f]+", re.IGNORECASE)


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


@dataclass
class TranscriptKnowledgeBase:
    transcript_dir: Path

    def __post_init__(self) -> None:
        self.records: list[dict] = []
        self.documents: dict[str, str] = {}
        for path in sorted(self.transcript_dir.glob("transcript-*-clean.md")):
            content = path.read_text(encoding="utf-8")
            self.documents[path.name] = content
            for citation, text in SEGMENT_RE.findall(content):
                cleaned = " ".join(text.split())
                if cleaned:
                    self.records.append(
                        {
                            "citation": citation,
                            "source": path.name,
                            "text": cleaned,
                        }
                    )

    def search(self, query: str, top_k: int = 6) -> list[dict]:
        return rank(query, self.records, top_k)

    def validate_selection(self, text: str, source: str) -> bool:
        document = self.documents.get(source)
        if not document:
            return False
        normalized_text = " ".join(text.casefold().split())
        normalized_document = " ".join(document.casefold().split())
        return bool(normalized_text) and normalized_text in normalized_document


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
