import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from embeddings import cosine_similarity, embed_chunks, get_embedding, load_cache, save_cache

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
TRANSCRIPT_DIR = ROOT / "data" / "vlearn-pack" / "transcript"
SLIDES_DIR = ROOT / "data" / "vlearn-pack" / "slides"


def load_env(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "export " in line:
            line = line.replace("export ", "", 1)
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def get_api_key(env: dict) -> str | None:
    for key in ("OPENAI_API_KEY", "OPENAI_APIKEY", "GOOGLE_API_KEY", "GEMINI_API_KEY", "API_KEY", "API key"):
        if key in env and env[key].strip():
            return env[key].strip()
    return None


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, source: str, chunk_type: str, page: int | None = None) -> list[dict]:
    chunks = []
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    for index, paragraph in enumerate(paragraphs):
        cleaned = normalize_text(paragraph)
        if len(cleaned) < 40:
            continue
        chunk_id = f"{source}#p{page}" if page is not None else f"{source}#chunk{index + 1}"
        chunks.append(
            {
                "source": source,
                "chunk_type": chunk_type,
                "chunk_id": chunk_id,
                "page": page,
                "text": cleaned[:1800],
            }
        )
    return chunks


def load_documents(transcript_dir: Path, slides_dir: Path) -> dict:
    """Nạp toàn bộ nội dung gốc theo từng nguồn (và từng trang với slide), dùng để đối chiếu khi validate."""
    documents: dict[str, dict] = {}

    for file_path in sorted(transcript_dir.glob("*.md")):
        if file_path.name.lower() == "readme.md":
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        if text.strip():
            documents[file_path.name] = {"chunk_type": "transcript", "full_text": text, "pages": {}}

    if slides_dir.exists():
        for file_path in sorted(slides_dir.glob("*.pdf")):
            try:
                from pypdf import PdfReader
            except Exception:
                continue
            try:
                reader = PdfReader(str(file_path))
            except Exception:
                continue
            pages: dict[int, str] = {}
            for page_number, page in enumerate(reader.pages, start=1):
                page_text = (page.extract_text() or "").strip()
                if page_text:
                    pages[page_number] = page_text
            if pages:
                documents[file_path.name] = {
                    "chunk_type": "slide",
                    "full_text": "\n\n".join(pages.values()),
                    "pages": pages,
                }

    return documents


def chunks_from_documents(documents: dict) -> list[dict]:
    chunks: list[dict] = []
    for source, doc in documents.items():
        if doc["pages"]:
            for page_number, page_text in doc["pages"].items():
                chunks.extend(chunk_text(page_text, source, doc["chunk_type"], page=page_number))
        else:
            chunks.extend(chunk_text(doc["full_text"], source, doc["chunk_type"]))
    return chunks


def load_chunks(transcript_dir: Path, slides_dir: Path) -> list[dict]:
    return chunks_from_documents(load_documents(transcript_dir, slides_dir))


def tokenize(text: str) -> list[str]:
    return [token for token in re.sub(r"[^a-z0-9\u00C0-\u024F]+", " ", text.lower()).split() if token]


def retrieve_chunks(query: str, chunks: list[dict], api_key: str, cache: dict, top_k: int = 4) -> list[dict]:
    if not query.strip():
        return []

    query_terms = set(tokenize(query))
    keyword_scored = []
    for chunk in chunks:
        text_terms = set(tokenize(chunk["text"]))
        overlap = len(query_terms & text_terms)
        if query_terms and " ".join(sorted(query_terms)) in chunk["text"].lower():
            overlap += 5
        if overlap > 0:
            keyword_scored.append((overlap, chunk))

    keyword_scored.sort(key=lambda item: item[0], reverse=True)
    candidates = [chunk for _, chunk in keyword_scored[:10]]

    if api_key and candidates:
        query_embedding = get_embedding(query, api_key)
        if query_embedding:
            chunk_embeddings = embed_chunks(candidates, api_key, cache)
            scored = []
            for chunk in candidates:
                chunk_embedding = chunk_embeddings.get(chunk["chunk_id"])
                if not chunk_embedding:
                    continue
                similarity = cosine_similarity(query_embedding, chunk_embedding)
                scored.append((similarity, chunk))
            if scored:
                scored.sort(key=lambda item: item[0], reverse=True)
                return [chunk for _, chunk in scored[:top_k]]

    return [chunk for _, chunk in keyword_scored[:top_k]]


def classify_query(query: str) -> str:
    text = query.lower().strip()
    if not text:
        return "empty"
    if len(text.split()) <= 2:
        return "too_short"
    sensitive_terms = ["password", "email", "phone", "address", "credit card", "api key", "secret", "personal"]
    if any(term in text for term in sensitive_terms):
        return "sensitive"
    if any(term in text for term in ["xin chào", "hello", "hi", "chào", "cảm ơn"]):
        return "greeting"
    if any(term in text for term in ["slide", "transcript", "bài giảng", "buổi học", "nội dung", "tóm tắt", "giải thích", "điểm chính", "ví dụ", "so sánh", "tại sao"]):
        return "course"
    return "out_of_scope"


def build_prompt(query: str, context_chunks: list[dict], guardrail: str) -> str:
    if guardrail in {"empty", "too_short", "sensitive"}:
        return (
            "Bạn là AI tutor cho VLearn. Hãy trả lời ngắn gọn bằng tiếng Việt. "
            "Nếu câu hỏi không rõ hoặc liên quan đến thông tin cá nhân, hãy đề nghị người dùng hỏi lại về nội dung bài giảng."
        )

    if guardrail == "out_of_scope":
        return (
            "Bạn là AI tutor cho VLearn. Hãy nói rõ rằng mình chỉ hỗ trợ trả lời về nội dung bài giảng và tài liệu học tập. "
            "Nếu người dùng hỏi ngoài phạm vi, hãy đề xuất một câu hỏi liên quan đến slide, transcript hoặc chủ đề học."
        )

    context_blocks = []
    for index, chunk in enumerate(context_chunks, start=1):
        context_blocks.append(f"[{index}] {cite_label(chunk)}\n{chunk['text']}")

    context_text = "\n\n".join(context_blocks) if context_blocks else "Không tìm thấy ngữ cảnh đủ cho câu hỏi này."

    return f"""Bạn là AI tutor cho nền tảng VLearn. Hãy trả lời bằng tiếng Việt.
Luôn dựa CHỈ trên tài liệu được cung cấp. Nếu không đủ thông tin, hãy nói rõ và đề xuất người dùng hỏi lại theo cách cụ thể.
Không bịa thêm thông tin. Không trả lời về thông tin cá nhân hoặc câu hỏi ngoài phạm vi học tập.
Luôn chèn trích dẫn nguồn ở cuối câu trả lời, dùng đúng nhãn trích dẫn đã cho trong tài liệu tham khảo (ví dụ [Trang 4] hoặc [Nguồn: tên file]).

Câu hỏi: {query}

Tài liệu tham khảo:
{context_text}

Hãy trả lời ngắn gọn, rõ ràng, có thể dùng bullet nếu cần."""


def cite_label(chunk: dict) -> str:
    if chunk.get("page") is not None:
        return f"Trang {chunk['page']} ({chunk['source']})"
    return f"Nguồn: {chunk['source']}"


def fallback_answer(query: str, context_chunks: list[dict], guardrail: str) -> str:
    if guardrail == "empty":
        return "Bạn có thể hỏi về một slide, một chủ đề, hoặc yêu cầu tóm tắt nội dung bài giảng. [Nguồn: hệ thống]"
    if guardrail in {"too_short", "sensitive"}:
        return "Mình chỉ hỗ trợ trả lời về nội dung bài giảng và tài liệu học tập. Hãy đặt câu hỏi cụ thể hơn về slide hoặc transcript. [Nguồn: hệ thống]"
    if guardrail == "out_of_scope":
        return "Mình chỉ hỗ trợ câu hỏi liên quan đến nội dung bài giảng của VLearn. Bạn có thể hỏi về tóm tắt bài học, một slide cụ thể, hoặc một chủ đề trong transcript. [Nguồn: hệ thống]"
    if not context_chunks:
        return "Mình chưa tìm thấy đủ ngữ cảnh trong dữ liệu để trả lời chắc chắn. Hãy hỏi về một phần cụ thể của bài giảng. [Nguồn: hệ thống]"

    top = context_chunks[0]
    snippet = normalize_text(top["text"][:450])
    return (
        f"Tôi chưa thể gọi mô hình AI lúc này, nhưng dựa trên tài liệu đã tải, câu trả lời gần nhất là: {snippet} "
        f"[{cite_label(top)}]"
    )


def call_openai(prompt: str, api_key: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 700,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in {401, 403, 429}:
            return ""
        raise
    except Exception:
        return ""

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return ""


def answer_query(query: str, api_key: str, chunks: list[dict], cache: dict) -> str:
    guardrail = classify_query(query)
    context_chunks = retrieve_chunks(query, chunks, api_key, cache, top_k=4)
    prompt = build_prompt(query, context_chunks, guardrail)
    response = call_openai(prompt, api_key) if api_key else ""
    if response.strip():
        return response.strip()
    return fallback_answer(query, context_chunks, guardrail)


def validate_selection(selected_text: str, source: str, page: int | None, documents: dict) -> str | None:
    """Đối chiếu đoạn bôi đen với dữ liệu tài liệu đã tải. Trả về thông báo lỗi nếu không khớp, None nếu hợp lệ."""
    doc = documents.get(source)
    if doc is None:
        return f"Không tìm thấy tài liệu '{source}' trong dữ liệu khoá học. Vui lòng chỉ bôi đen đoạn đang hiển thị trên trang học."

    if page is not None:
        page_text = doc["pages"].get(page)
        if page_text is None:
            return f"Trang {page} không tồn tại trong tài liệu '{source}'."
        reference_text = page_text
    else:
        reference_text = doc["full_text"]

    normalized_selection = normalize_text(selected_text).lower()
    normalized_reference = normalize_text(reference_text).lower()

    if normalized_selection and normalized_selection in normalized_reference:
        return None

    selection_tokens = set(tokenize(selected_text))
    reference_tokens = set(tokenize(reference_text))
    if selection_tokens:
        overlap_ratio = len(selection_tokens & reference_tokens) / len(selection_tokens)
        if overlap_ratio >= 0.8:
            return None

    return "Đoạn bôi đen không khớp với nội dung tài liệu đã tải. Vui lòng chỉ bôi đen text đang hiển thị trên trang học (không tự nhập đoạn khác)."


def classify_highlight_query(question: str) -> str:
    guardrail = classify_query(question)
    if guardrail == "out_of_scope":
        return "course"
    return guardrail


def build_highlight_prompt(
    question: str,
    selection: dict,
    related_chunks: list[dict],
    guardrail: str,
) -> str:
    if guardrail in {"empty", "too_short", "sensitive"}:
        return (
            "Bạn là AI tutor cho VLearn. Hãy trả lời ngắn gọn bằng tiếng Việt. "
            "Nếu câu hỏi không rõ hoặc liên quan đến thông tin cá nhân, hãy đề nghị người dùng hỏi lại về đoạn đã bôi đen."
        )

    if guardrail == "out_of_scope":
        return (
            "Bạn là AI tutor cho VLearn. Hãy nói rõ rằng mình chỉ hỗ trợ trả lời về đoạn tài liệu học viên vừa bôi đen. "
            "Nếu người dùng hỏi ngoài phạm vi, hãy đề xuất họ hỏi về nội dung đoạn đã chọn."
        )

    selection_label = cite_label(selection)
    related_blocks = [f"[{cite_label(chunk)}]\n{chunk['text']}" for chunk in related_chunks]
    related_text = "\n\n".join(related_blocks) if related_blocks else "Không có."

    return f"""Bạn là AI tutor cho nền tảng VLearn, đang hỗ trợ học viên ngay trong trang học.
Học viên vừa BÔI ĐEN một đoạn tài liệu (đoạn chính bên dưới) rồi đặt câu hỏi về đoạn đó.
Hãy trả lời DỰA TRƯỚC HẾT vào đoạn đã bôi đen; chỉ dùng tài liệu liên quan thêm để bổ sung ngữ cảnh, không thay thế đoạn chính.
Nếu đoạn đã bôi đen không đủ để trả lời, hãy nói rõ là chưa đủ thông tin thay vì bịa.
Không trả lời về thông tin cá nhân hoặc câu hỏi ngoài phạm vi học tập.
Luôn chèn trích dẫn nguồn ở cuối câu trả lời theo đúng nhãn đã cho, ví dụ [{selection_label}].

Câu hỏi: {question}

Đoạn học viên đã bôi đen [{selection_label}]:
{selection['text']}

Tài liệu liên quan khác (nếu cần):
{related_text}

Hãy trả lời ngắn gọn, rõ ràng, có thể dùng bullet nếu cần."""


def fallback_highlight_answer(selection: dict, guardrail: str) -> str:
    if guardrail in {"empty", "too_short", "sensitive"}:
        return "Hãy đặt một câu hỏi cụ thể về đoạn bạn vừa bôi đen. [Nguồn: hệ thống]"
    if guardrail == "out_of_scope":
        return "Mình chỉ hỗ trợ câu hỏi liên quan đến đoạn bạn vừa bôi đen. Hãy hỏi lại về nội dung đó. [Nguồn: hệ thống]"

    snippet = normalize_text(selection["text"][:450])
    return (
        f"Tôi chưa thể gọi mô hình AI lúc này, nhưng đoạn bạn bôi đen có nội dung: {snippet} "
        f"[{cite_label(selection)}]"
    )


def answer_highlight(
    question: str,
    selected_text: str,
    source: str,
    page: int | None,
    api_key: str,
    chunks: list[dict],
    documents: dict,
    cache: dict,
) -> str:
    selection = {"source": source, "chunk_type": "highlight", "page": page, "text": normalize_text(selected_text)}
    if not selection["text"]:
        return "Chưa nhận được đoạn bôi đen nào. Hãy chọn một đoạn tài liệu trước khi hỏi. [Nguồn: hệ thống]"

    validation_error = validate_selection(selected_text, source, page, documents)
    if validation_error:
        return f"{validation_error} [Nguồn: hệ thống]"

    guardrail = classify_highlight_query(question)
    same_source_chunks = [c for c in chunks if c["source"] == source]
    related_chunks = retrieve_chunks(question, same_source_chunks or chunks, api_key, cache, top_k=2)
    prompt = build_highlight_prompt(question, selection, related_chunks, guardrail)
    response = call_openai(prompt, api_key) if api_key else ""
    if response.strip():
        return response.strip()
    return fallback_highlight_answer(selection, guardrail)


def main() -> None:
    parser = argparse.ArgumentParser(description="Chatbot tutor cho VLearn")
    parser.add_argument("query", nargs="*", help="Câu hỏi của học viên")
    parser.add_argument("--interactive", action="store_true", help="Chạy ở chế độ hội thoại")
    parser.add_argument("--highlight", help="Đoạn tài liệu học viên đã bôi đen")
    parser.add_argument("--source", help="Tên file nguồn của đoạn bôi đen (vd: slide-03.pdf)")
    parser.add_argument("--page", type=int, help="Số trang của đoạn bôi đen (nếu là slide)")
    args = parser.parse_args()

    env = load_env(ENV_PATH)
    api_key = get_api_key(env)
    documents = load_documents(TRANSCRIPT_DIR, SLIDES_DIR)
    chunks = chunks_from_documents(documents)
    cache = load_cache()

    if not chunks:
        print("Không tìm thấy dữ liệu transcript hoặc slide để xây chatbot.")
        sys.exit(1)

    try:
        if args.highlight is not None:
            question = " ".join(args.query) if args.query else input("Bạn muốn hỏi gì về đoạn đã bôi đen? \n").strip()
            source = args.source or "đoạn bôi đen"
            print("\n=== Câu trả lời ===\n")
            print(answer_highlight(question, args.highlight, source, args.page, api_key, chunks, documents, cache))
            return

        if args.interactive:
            print("Chatbot VLearn đang chạy. Gõ 'quit' để thoát.")
            while True:
                query = input("\nBạn hỏi: ").strip()
                if query.lower() in {"quit", "exit", "q"}:
                    break
                print("\n=== Câu trả lời ===\n")
                print(answer_query(query, api_key, chunks, cache))
            return

        if args.query:
            query = " ".join(args.query)
        else:
            query = input("Bạn muốn hỏi về nội dung bài giảng gì? \n").strip()

        print("\n=== Câu trả lời ===\n")
        print(answer_query(query, api_key, chunks, cache))
    finally:
        if cache:
            save_cache(cache)


if __name__ == "__main__":
    main()
