"""Tạo chunk metadata và vector embedding phục vụ hai tool hỏi đáp."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from backend.app.core.config import Settings
from backend.app.data_processing.chunking import chunk_transcript


DAY_MAPPING = {
    "day-1": ["transcript-04-clean.md", "transcript-06-clean.md"],
    "day-2": [
        "transcript-01-clean.md",
        "transcript-02-clean.md",
        "transcript-03-clean.md",
        "transcript-05-clean.md",
    ],
}


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )


def load_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_chunks(
    settings: Settings,
    *,
    target_chars: int,
    overlap_chars: int,
) -> list[dict]:
    chunks: list[dict] = []
    for day, filenames in DAY_MAPPING.items():
        for filename in filenames:
            path = settings.transcript_dir / filename
            if not path.is_file():
                raise FileNotFoundError(f"Không tìm thấy {path}.")
            chunks.extend(
                chunk_transcript(
                    path,
                    day=day,
                    target_chars=target_chars,
                    overlap_chars=overlap_chars,
                )
            )
    return chunks


def embed_chunks(
    settings: Settings,
    chunks: list[dict],
    *,
    force: bool = False,
    batch_size: int = 64,
) -> list[dict]:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Thiếu OPENAI_API_KEY để tạo embeddings.")
    from openai import OpenAI

    cached = {
        record["id"]: record
        for record in load_jsonl(settings.vector_index)
        if record.get("model") == settings.embedding_model
        and record.get("dimensions") == settings.embedding_dimensions
    }
    vectors: dict[str, dict] = {}
    pending: list[dict] = []
    for chunk in chunks:
        old = cached.get(chunk["id"])
        if (
            not force
            and old
            and old.get("content_hash") == chunk["metadata"]["content_hash"]
        ):
            vectors[chunk["id"]] = old
        else:
            pending.append(chunk)

    client = OpenAI()
    for offset in range(0, len(pending), batch_size):
        batch = pending[offset : offset + batch_size]
        response = client.embeddings.create(
            model=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
            input=[chunk["text"] for chunk in batch],
        )
        for chunk, item in zip(batch, response.data):
            vectors[chunk["id"]] = {
                "id": chunk["id"],
                "content_hash": chunk["metadata"]["content_hash"],
                "model": settings.embedding_model,
                "dimensions": settings.embedding_dimensions,
                "embedding": item.embedding,
            }
        print(f"[embed] {min(offset + len(batch), len(pending))}/{len(pending)}")
    return [vectors[chunk["id"]] for chunk in chunks]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-chars", type=int, default=700)
    parser.add_argument("--overlap-chars", type=int, default=100)
    parser.add_argument(
        "--chunks-only",
        action="store_true",
        help="Chỉ ghi chunks + metadata, không gọi Embeddings API.",
    )
    parser.add_argument("--check", action="store_true", help="Kiểm tra, không ghi file.")
    parser.add_argument("--force", action="store_true", help="Tạo lại mọi vector.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = Settings.from_env()
    chunks = build_chunks(
        settings,
        target_chars=args.target_chars,
        overlap_chars=args.overlap_chars,
    )
    if not chunks:
        raise RuntimeError("Không tạo được chunk nào.")
    print(
        f"[ok] {len(chunks)} chunks; "
        f"target={args.target_chars}, overlap={args.overlap_chars}"
    )
    if args.check:
        return 0

    write_jsonl(settings.chunk_index, chunks)
    manifest = {
        "version": 1,
        "chunk_count": len(chunks),
        "target_chars": args.target_chars,
        "overlap_chars": args.overlap_chars,
        "embedding_model": settings.embedding_model,
        "embedding_dimensions": settings.embedding_dimensions,
    }
    manifest_path = settings.chunk_index.parent / "index.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[ok] {settings.chunk_index}")
    if not args.chunks_only:
        vectors = embed_chunks(settings, chunks, force=args.force)
        write_jsonl(settings.vector_index, vectors)
        print(f"[ok] {settings.vector_index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
