import os
from dataclasses import dataclass
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]
CODEBASE_DIR = BACKEND_DIR.parent
PROJECT_ROOT = CODEBASE_DIR.parent


def load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key:
            os.environ.setdefault(key, value)


@dataclass(frozen=True)
class Settings:
    project_root: Path
    data_dir: Path
    transcript_dir: Path
    summary_dir: Path
    summary_index: Path
    chunk_index: Path
    vector_index: Path
    openai_model: str
    quiz_model: str
    summary_model: str
    embedding_model: str
    embedding_dimensions: int
    reasoning_effort: str
    cors_origins: tuple[str, ...]

    @classmethod
    def from_env(cls) -> "Settings":
        load_env_file(PROJECT_ROOT / ".env")
        load_env_file(BACKEND_DIR / ".env")
        origins = tuple(
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:3000,http://localhost:5173",
            ).split(",")
            if origin.strip()
        )
        data_dir = BACKEND_DIR / "data"
        processed_dir = data_dir / "processed"
        default_model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
        return cls(
            project_root=PROJECT_ROOT,
            data_dir=data_dir,
            transcript_dir=data_dir / "raw" / "vlearn-pack" / "transcript",
            summary_dir=processed_dir / "summaries",
            summary_index=processed_dir / "summary-index.json",
            chunk_index=processed_dir / "embeddings" / "chunks.jsonl",
            vector_index=processed_dir / "embeddings" / "vectors.jsonl",
            openai_model=os.getenv("OPENAI_BACKEND_MODEL", default_model),
            quiz_model=os.getenv("OPENAI_QUIZ_MODEL", default_model),
            summary_model=os.getenv("OPENAI_SUMMARY_MODEL", default_model),
            embedding_model=os.getenv(
                "OPENAI_EMBEDDING_MODEL",
                "text-embedding-3-small",
            ),
            embedding_dimensions=int(
                os.getenv("OPENAI_EMBEDDING_DIMENSIONS", "1024")
            ),
            reasoning_effort=os.getenv("OPENAI_REASONING_EFFORT", "low"),
            cors_origins=origins,
        )
