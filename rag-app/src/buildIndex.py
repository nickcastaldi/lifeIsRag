"""
Build OWASP RAG index from cloned GitHub repos.
Run once after cloning. Re-run to refresh after pulling repo updates.
Uses local embeddings (no API keys needed).
"""
import os
import pickle
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

# Config
DOCS_DIR = "owasp_rag_docs"
INDEX_DIR = "owasp_index"
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# Files to skip (noise)
SKIP_PATTERNS = [
    "readme.md", "contributing.md", "code_of_conduct.md",
    "license", "changelog.md", "security.md", "info.md",
    ".github/", "node_modules/", "_includes/", "_layouts/",
    "assets/", "_sass/",
]

NON_ENGLISH_LANGS = [
    "/fr/", "/es/", "/de/", "/ja/", "/zh/", "/pt/", "/it/",
    "/ko/", "/ru/", "/ar/", "/he/", "/hi/", "/tr/", "/pl/",
    "-ja.md", "-fr.md", "-es.md", "-de.md", "-zh.md",
]


def should_skip_file(file_path: Path) -> bool:
    path_str = str(file_path).lower().replace("\\", "/")
    for pattern in SKIP_PATTERNS:
        if pattern.lower() in path_str:
            return True
    for lang in NON_ENGLISH_LANGS:
        if lang in path_str:
            return True
    return False


def load_all_markdown(base_dir: str = DOCS_DIR):
    base_path = Path(base_dir)
    if not base_path.exists():
        raise FileNotFoundError(f"Directory {base_dir} not found.")

    all_docs = []
    repo_counts = {}

    for repo_dir in base_path.iterdir():
        if not repo_dir.is_dir():
            continue

        repo_name = repo_dir.name
        repo_docs = []

        for md_file in repo_dir.rglob("*.md"):
            if should_skip_file(md_file):
                continue

            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                if len(content.strip()) < 100:
                    continue

                doc = Document(
                    page_content=content,
                    metadata={
                        "source": str(md_file.relative_to(base_path)),
                        "repo": repo_name,
                        "filename": md_file.name,
                    }
                )
                repo_docs.append(doc)
            except Exception as e:
                print(f"  WARN: Skipping {md_file}: {e}")

        repo_counts[repo_name] = len(repo_docs)
        all_docs.extend(repo_docs)

    print("\nDocuments loaded by repo:")
    for repo, count in sorted(repo_counts.items(), key=lambda x: -x[1]):
        print(f"  {count:>4} files - {repo}")
    print(f"\nTotal: {len(all_docs)} markdown files\n")

    return all_docs


def chunk_documents(docs):
    headers_to_split = [("#", "h1"), ("##", "h2"), ("###", "h3")]
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    final_chunks = []
    for doc in docs:
        try:
            header_chunks = md_splitter.split_text(doc.page_content)
            for chunk in header_chunks:
                combined_metadata = {**doc.metadata, **chunk.metadata}
                if len(chunk.page_content) > CHUNK_SIZE:
                    sub_chunks = text_splitter.split_text(chunk.page_content)
                    for sub_chunk in sub_chunks:
                        final_chunks.append(Document(
                            page_content=sub_chunk,
                            metadata=combined_metadata
                        ))
                else:
                    chunk.metadata = combined_metadata
                    final_chunks.append(chunk)
        except Exception:
            sub_chunks = text_splitter.split_text(doc.page_content)
            for sub_chunk in sub_chunks:
                final_chunks.append(Document(
                    page_content=sub_chunk,
                    metadata=doc.metadata
                ))

    print(f"Created {len(final_chunks)} chunks")
    return final_chunks


def build_faiss_index(chunks):
    print(f"\nCreating embeddings using {EMBEDDING_MODEL}...")
    print("  (First run downloads the model, ~130 MB)")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )

    print("  Embedding chunks (this is the slow part on CPU)...")
    vector_store = FAISS.from_documents(chunks, embeddings)

    os.makedirs(INDEX_DIR, exist_ok=True)
    vector_store.save_local(INDEX_DIR)
    print(f"FAISS index saved to {INDEX_DIR}/")

    return vector_store


def build_bm25_index(chunks):
    print("\nCreating BM25 index...")
    tokenized_chunks = [chunk.page_content.lower().split() for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)

    bm25_data = {"bm25": bm25, "chunks": chunks}
    bm25_path = os.path.join(INDEX_DIR, "bm25.pkl")
    with open(bm25_path, "wb") as f:
        pickle.dump(bm25_data, f)

    print(f"BM25 index saved to {bm25_path}")


def main():
    print("Building OWASP RAG index (fully local, no API)...\n")
    docs = load_all_markdown()
    chunks = chunk_documents(docs)
    build_faiss_index(chunks)
    build_bm25_index(chunks)
    print("\nDone! Next: run `python query.py`")


if __name__ == "__main__":
    main()
