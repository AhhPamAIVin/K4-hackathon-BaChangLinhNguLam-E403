import hashlib
import json
from pathlib import Path

import urllib.request

ROOT = Path(__file__).resolve().parent
CACHE_PATH = ROOT / "data" / "embedding_cache.json"
EMBEDDING_MODEL = "text-embedding-3-small"


def get_embedding(text: str, api_key: str) -> list[float] | None:
    if not text.strip() or not api_key:
        return None
    url = "https://api.openai.com/v1/embeddings"
    payload = {"model": EMBEDDING_MODEL, "input": text[:8000]}
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None

    try:
        return data["data"][0]["embedding"]
    except (KeyError, IndexError, TypeError):
        return None


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cache(path: Path = CACHE_PATH) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_cache(cache: dict, path: Path = CACHE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")


def get_chunk_embedding(chunk_id: str, text: str, api_key: str, cache: dict) -> list[float] | None:
    """Trả embedding từ cache nếu nội dung chunk chưa đổi; ngược lại gọi API và lưu lại cache."""
    content_hash = _content_hash(text)
    entry = cache.get(chunk_id)
    if entry and entry.get("hash") == content_hash:
        return entry.get("embedding")

    embedding = get_embedding(text, api_key)
    if embedding is not None:
        cache[chunk_id] = {"hash": content_hash, "embedding": embedding}
    return embedding


def embed_chunks(chunks: list[dict], api_key: str, cache: dict) -> dict[str, list[float]]:
    """Đảm bảo mọi chunk trong danh sách đều có embedding trong cache, trả về map chunk_id -> embedding."""
    result = {}
    for chunk in chunks:
        embedding = get_chunk_embedding(chunk["chunk_id"], chunk["text"], api_key, cache)
        if embedding is not None:
            result[chunk["chunk_id"]] = embedding
    return result
