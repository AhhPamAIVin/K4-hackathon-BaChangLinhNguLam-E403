import sys

from chatbot import ENV_PATH, SLIDES_DIR, TRANSCRIPT_DIR, chunks_from_documents, get_api_key, load_documents, load_env
from embeddings import get_chunk_embedding, load_cache, prune_cache, save_cache

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def main() -> None:
    env = load_env(ENV_PATH)
    api_key = get_api_key(env)
    if not api_key:
        print("Không tìm thấy API key trong .env.")
        sys.exit(1)

    documents = load_documents(TRANSCRIPT_DIR, SLIDES_DIR)
    chunks = chunks_from_documents(documents)
    print(f"Tổng số chunk cần embed: {len(chunks)} (từ {len(documents)} tài liệu)")

    cache = load_cache()
    hits = 0
    misses = 0
    failed = 0

    for index, chunk in enumerate(chunks, start=1):
        already_cached = chunk["chunk_id"] in cache
        embedding = get_chunk_embedding(chunk, api_key, cache)
        if embedding is None:
            failed += 1
            print(f"  [{index}/{len(chunks)}] LỖI: {chunk['chunk_id']}")
        elif already_cached:
            hits += 1
        else:
            misses += 1
            if misses % 20 == 0:
                save_cache(cache)
                print(f"  [{index}/{len(chunks)}] đã embed {misses} chunk mới, lưu tạm cache...")

    valid_chunk_ids = {chunk["chunk_id"] for chunk in chunks}
    pruned = prune_cache(cache, valid_chunk_ids)

    save_cache(cache)
    print(
        f"\nXong. Cache hit: {hits}, embed mới: {misses}, lỗi: {failed}, "
        f"đã xoá {pruned} chunk cũ không còn tồn tại, tổng entry trong cache: {len(cache)}"
    )


if __name__ == "__main__":
    main()
