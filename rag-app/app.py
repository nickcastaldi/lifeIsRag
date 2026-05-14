"""
RAG application — Phase 2 artifact.

Run locally:
  ollama pull llama3.1
  uvicorn app:api --reload --port 8000

POST /query  {"question": "..."}  → {"answer": "...", "sources": [...]}
POST /ingest  {"path": "docs/"}   → ingests documents into the vector store
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
DOCS_DIR = os.getenv("DOCS_DIR", "./docs")

# System prompt — intentionally visible here so Phase 3 prompt injection tests
# can verify whether it leaks through indirect injection vectors.
SYSTEM_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are a helpful assistant. Answer using only the provided context.\n"
        "If the answer is not in the context, say you don't know.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    ),
)

embeddings = OllamaEmbeddings(model=EMBED_MODEL)
llm = OllamaLLM(model=MODEL, temperature=0)

vectorstore: Chroma | None = None


def get_vectorstore() -> Chroma:
    global vectorstore
    if vectorstore is None:
        vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings,
        )
    return vectorstore


def build_chain() -> RetrievalQA:
    vs = get_vectorstore()
    retriever = vs.as_retriever(search_kwargs={"k": 4})
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": SYSTEM_PROMPT},
        return_source_documents=True,
    )


api = FastAPI(title="RAG Security Lab", version="0.1.0")


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


class IngestRequest(BaseModel):
    path: str = DOCS_DIR


@api.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")
    chain = build_chain()
    result = chain.invoke({"query": req.question})
    sources = [
        doc.metadata.get("source", "unknown")
        for doc in result.get("source_documents", [])
    ]
    return QueryResponse(answer=result["result"], sources=list(dict.fromkeys(sources)))


@api.post("/ingest")
def ingest(req: IngestRequest) -> dict:
    docs_path = Path(req.path)
    if not docs_path.exists():
        raise HTTPException(status_code=404, detail=f"path not found: {docs_path}")

    loader = DirectoryLoader(str(docs_path), loader_cls=TextLoader, silent_errors=True)
    raw_docs = loader.load()
    if not raw_docs:
        raise HTTPException(status_code=422, detail="no documents found in path")

    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
    chunks = splitter.split_documents(raw_docs)

    vs = get_vectorstore()
    vs.add_documents(chunks)
    return {"ingested": len(chunks), "source_files": len(raw_docs)}


@api.get("/health")
def health() -> dict:
    return {"status": "ok", "model": MODEL}
