import argparse
import json
import re
import sys
from pathlib import Path

from chatbot import (
    ENV_PATH,
    SLIDES_DIR,
    TRANSCRIPT_DIR,
    cite_label,
    call_openai,
    get_api_key,
    load_documents,
    load_env,
    normalize_text,
)
from embeddings import cosine_similarity, embed_chunks, load_cache, save_cache

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "quiz-output"

MIN_CHUNK_LEN = 80


def collect_quiz_chunks(source: str, documents: dict) -> list[dict]:
    """Lấy các đoạn đủ dài của một nguồn (slide/transcript) để làm ứng viên sinh câu hỏi."""
    doc = documents.get(source)
    if doc is None:
        return []

    chunks: list[dict] = []
    if doc["pages"]:
        for page_number, page_text in doc["pages"].items():
            for index, paragraph in enumerate(re.split(r"\n\s*\n", page_text)):
                cleaned = normalize_text(paragraph)
                if len(cleaned) < MIN_CHUNK_LEN:
                    continue
                chunks.append(
                    {
                        "chunk_id": f"{source}#p{page_number}#{index}",
                        "source": source,
                        "page": page_number,
                        "text": cleaned[:1800],
                    }
                )
    else:
        for index, paragraph in enumerate(re.split(r"\n\s*\n", doc["full_text"])):
            cleaned = normalize_text(paragraph)
            if len(cleaned) < MIN_CHUNK_LEN:
                continue
            chunks.append(
                {
                    "chunk_id": f"{source}#c{index}",
                    "source": source,
                    "page": None,
                    "text": cleaned[:1800],
                }
            )
    return chunks


def select_diverse_chunks(chunks: list[dict], embeddings_map: dict[str, list[float]], num: int) -> list[dict]:
    """Chọn `num` chunk trải đều chủ đề bằng farthest-point sampling trên embedding, tránh câu hỏi trùng ý."""
    usable = [c for c in chunks if c["chunk_id"] in embeddings_map]
    if len(usable) <= num:
        return usable

    selected = [usable[0]]
    remaining = usable[1:]

    while len(selected) < num and remaining:
        best_chunk = None
        best_score = -1.0
        for candidate in remaining:
            candidate_emb = embeddings_map[candidate["chunk_id"]]
            min_similarity = min(
                cosine_similarity(candidate_emb, embeddings_map[s["chunk_id"]]) for s in selected
            )
            if min_similarity > best_score:
                best_score = min_similarity
                best_chunk = candidate
        selected.append(best_chunk)
        remaining.remove(best_chunk)

    return selected


def build_quiz_prompt(chunk: dict) -> str:
    label = cite_label(chunk)
    return f"""Bạn là AI tạo đề kiểm tra hiểu bài cuối buổi cho nền tảng học tập VLearn.
Dựa CHỈ trên đoạn tài liệu dưới đây, hãy tạo đúng 1 câu hỏi trắc nghiệm kiểm tra hiểu thật (không phải học vẹt), có 4 phương án A/B/C/D, chỉ 1 đáp án đúng.
Không hỏi những chi tiết vụn vặt (số liệu, tên riêng không quan trọng); ưu tiên hỏi về ý nghĩa, bản chất, cách áp dụng.
Trả lời DUY NHẤT một JSON hợp lệ, không thêm chữ nào khác, đúng format:
{{"question": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "answer": "A", "explanation": "..."}}

Đoạn tài liệu [{label}]:
{chunk['text']}"""


def parse_quiz_json(raw: str) -> dict | None:
    if not raw:
        return None
    text = raw.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    else:
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(0)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None
    if "question" not in data or "options" not in data or "answer" not in data:
        return None
    if data["answer"] not in data["options"]:
        return None
    return data


def generate_quiz(source: str, num: int, api_key: str, documents: dict, cache: dict) -> list[dict]:
    candidates = collect_quiz_chunks(source, documents)
    if not candidates:
        return []

    embeddings_map = embed_chunks(candidates, api_key, cache)
    if not embeddings_map:
        selected = candidates[:num]
    else:
        selected = select_diverse_chunks(candidates, embeddings_map, num)

    quiz_items = []
    for chunk in selected:
        prompt = build_quiz_prompt(chunk)
        response = call_openai(prompt, api_key)
        quiz_data = parse_quiz_json(response)
        if quiz_data is None:
            continue
        quiz_data["citation"] = cite_label(chunk)
        quiz_data["source_chunk_id"] = chunk["chunk_id"]
        quiz_items.append(quiz_data)

    return quiz_items


def print_quiz(quiz_items: list[dict]) -> None:
    for index, item in enumerate(quiz_items, start=1):
        print(f"\nCâu {index}: {item['question']}")
        for label, option_text in item["options"].items():
            print(f"  {label}. {option_text}")
        print(f"  Đáp án đúng: {item['answer']}")
        if item.get("explanation"):
            print(f"  Giải thích: {item['explanation']}")
        print(f"  [{item['citation']}]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sinh đề kiểm tra cuối slide từ dữ liệu VLearn, tái dùng embedding cache của chatbot")
    parser.add_argument("--source", required=True, help="Tên file slide/transcript cần tạo đề (vd: d2-slide-hackathon.pdf)")
    parser.add_argument("--num", type=int, default=5, help="Số câu hỏi muốn tạo (mặc định 5)")
    args = parser.parse_args()

    env = load_env(ENV_PATH)
    api_key = get_api_key(env)
    if not api_key:
        print("Không tìm thấy API key trong .env.")
        sys.exit(1)

    documents = load_documents(TRANSCRIPT_DIR, SLIDES_DIR)
    if args.source not in documents:
        available = ", ".join(sorted(documents.keys()))
        print(f"Không tìm thấy nguồn '{args.source}'. Các nguồn hiện có: {available}")
        sys.exit(1)

    cache = load_cache()
    try:
        quiz_items = generate_quiz(args.source, args.num, api_key, documents, cache)
    finally:
        save_cache(cache)

    if not quiz_items:
        print("Không tạo được câu hỏi nào (đoạn tài liệu quá ngắn hoặc lỗi gọi mô hình).")
        sys.exit(1)

    print_quiz(quiz_items)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{Path(args.source).stem}-quiz.json"
    output_path.write_text(json.dumps(quiz_items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nĐã lưu đề kiểm tra vào {output_path}")


if __name__ == "__main__":
    main()
