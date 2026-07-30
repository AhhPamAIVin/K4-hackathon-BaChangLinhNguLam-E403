import os
from dataclasses import dataclass
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


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
    transcript_dir: Path
    summary_dir: Path
    summary_index: Path
    openai_model: str
    reasoning_effort: str
    cors_origins: tuple[str, ...]

    @classmethod
    def from_env(cls) -> "Settings":
        load_env_file(PROJECT_ROOT / ".env")
        load_env_file(PROJECT_ROOT / "feature" / "question" / ".env")
        origins = tuple(
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:3000,http://localhost:5173",
            ).split(",")
            if origin.strip()
        )
        output_dir = PROJECT_ROOT / "feature" / "question" / "output"
        return cls(
            project_root=PROJECT_ROOT,
            transcript_dir=PROJECT_ROOT / "data" / "vlearn-pack" / "transcript",
            summary_dir=output_dir / "summaries",
            summary_index=output_dir / "summary-index.json",
            openai_model=os.getenv(
                "OPENAI_BACKEND_MODEL",
                os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
            ),
            reasoning_effort=os.getenv("OPENAI_REASONING_EFFORT", "low"),
            cors_origins=origins,
        )
