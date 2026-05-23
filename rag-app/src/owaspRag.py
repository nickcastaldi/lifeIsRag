"""
OWASP RAG with hybrid search, reranking, and local Llama.
"""
import os
import pickle
import numpy as np
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from sentence_transformers import CrossEncoder

INDEX_DIR = "owasp_index"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
LLAMA_MODEL = "llama3.2:3b"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class OWASPRagApp:
    def __init__(self):
        print("Loading OWASP RAG...")

        # Load embeddings (same model used for indexing)
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            encode_kwargs={"normalize_embeddings": True},
        )

        # Load FAISS
        self.vector_store = FAISS.load_local(
            INDEX_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )

        # Load BM25 + chunks
        bm25_path = Path(INDEX_DIR) / "bm25.pkl"
        with open(bm25_path, "rb") as f:
            bm25_data = pickle.load(f)
        self.bm25 = bm25_data["bm25"]
        self.chunks = bm25_data["chunks"]

        # Cross-encoder for reranking (smaller model for low-RAM)
        print("Loading cross-encoder reranker...")
        self.reranker = CrossEncoder(RERANKER_MODEL, max_length=512)

        # Llama via Ollama
        print(f"Connecting to Ollama ({LLAMA_MODEL})...")
        self.llm = ChatOllama(
            model=LLAMA_MODEL,
            temperature=0.1,
            base_url="http://localhost:11434",
        )

        print("Ready!\n")

    def _bm25_search(self, query, k=20):
        tokenized = query.lower().split()
        scores = self.bm25.get_scores(tokenized)
        top_k_indices = np.argsort(scores)[::-1][:k]
        return [(self.chunks[i], scores[i]) for i in top_k_indices]

    def _faiss_search(self, query, k=20):
        return self.vector_store.similarity_search_with_score(query, k=k)

    def _reciprocal_rank_fusion(self, bm25_results, faiss_results, k_rrf=60):
        rrf_scores = {}
        for rank, (doc, _) in enumerate(bm25_results):
            doc_id = doc.page_content[:100]
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = {"score": 0, "doc": doc}
            rrf_scores[doc_id]["score"] += 1 / (rank + k_rrf)
        for rank, (doc, _) in enumerate(faiss_results):
            doc_id = doc.page_content[:100]
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = {"score": 0, "doc": doc}
            rrf_scores[doc_id]["score"] += 1 / (rank + k_rrf)
        sorted_results = sorted(
            rrf_scores.values(),
            key=lambda x: x["score"],
            reverse=True
        )
        return [item["doc"] for item in sorted_results]

    def _rerank(self, query, docs, top_k=5):
        if not docs:
            return []
        pairs = [[query, doc.page_content] for doc in docs]
        scores = self.reranker.predict(pairs)
        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in ranked[:top_k]]

    def retrieve(self, query, top_k=5, retrieval_k=20):
        bm25_results = self._bm25_search(query, k=retrieval_k)
        faiss_results = self._faiss_search(query, k=retrieval_k)
        fused = self._reciprocal_rank_fusion(bm25_results, faiss_results)
        return self._rerank(query, fused[:retrieval_k], top_k=top_k)

    def answer(self, query):
        docs = self.retrieve(query, top_k=5)

        context = "\n\n---\n\n".join([
            f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
            for doc in docs
        ])

        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a security expert specializing in OWASP standards. Answer using ONLY the provided context.

If the context doesn't contain enough information, say "I couldn't find that in the OWASP documentation."

Context:
{context}

Question: {question}

Provide a clear, technical answer. Cite specific OWASP documents (e.g., "OWASP Top 10 A03:2021", "ASVS Section 5.1") when relevant.

Answer:"""
        )

        prompt = prompt_template.format(context=context, question=query)
        response = self.llm.invoke(prompt)

        return {
            "answer": response.content,
            "sources": [d.metadata for d in docs],
        }
