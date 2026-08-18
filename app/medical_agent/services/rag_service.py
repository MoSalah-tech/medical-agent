"""
RAG service: PDF ingestion, chunking, embedding, and retrieval.

Vector store: pgvector (via langchain-postgres), not FAISS — see the
FAISS-vs-pgvector rationale discussed alongside this file. Every document
is tagged with `user_id` in its metadata, and every search is filtered by
`user_id`, so one user's uploaded documents can never surface in another
user's retrieval results.
"""

import logging
from typing import Optional

from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_postgres import PGVector
from langchain_community.vectorstores import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from psycopg_pool import ConnectionPool
from pypdf import PdfReader

from app.medical_agent.core.config import *

logger = logging.getLogger(__name__)

_embeddings: Optional[GoogleGenerativeAIEmbeddings] = None
_vectorstore: Optional[PGVector] = None
_pool: Optional[ConnectionPool] = None

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " ", ""],
)


class RAGError(Exception):
    pass


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        if embedding_provider != "gemini":
            raise RAGError(f"Unsupported embedding provider: {embedding_provider}")
        _embeddings = GoogleGenerativeAIEmbeddings(
            model=gemini_embedding_model,
            google_api_key=gemini_api_key,
        )
    return _embeddings


def get_vectorstore() -> PGVector:
    """
    Lazily builds a single PGVector client, reused across requests.
    PGVector manages its own connection pool internally, so this is safe
    to share across concurrent requests within one process.
    """
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = PGVector(
            embeddings=get_embeddings(),
            collection_name=pgvector_collection,
            connection=database_url_psycopg,
            use_jsonb=True,
        )
    return _vectorstore


def _get_pool() -> ConnectionPool:
    """A small pooled psycopg connection, separate from PGVector's own
    internals, used only for the cheap existence check below. Opened once
    and reused — avoids paying connection-setup cost on every chat turn."""
    global _pool
    if _pool is None:
        _pool = ConnectionPool(database_url_psycopg, min_size=1, max_size=5, open=True)
    return _pool


def user_has_documents(user_id: str) -> bool:
    """
    Cheap existence check: does this user have *any* ingested chunks at all?

    This exists so retrieval can be skipped entirely for users who've never
    uploaded anything — no embedding call, no similarity search, the agent
    just behaves like a normal chat. Deliberately a raw SQL EXISTS query
    against langchain-postgres's own tables rather than a similarity_search
    call, since the latter would cost an embedding API call just to answer
    a yes/no question.
    """
    query = """
        SELECT 1
        FROM langchain_pg_embedding e
        JOIN langchain_pg_collection c ON e.collection_id = c.uuid
        WHERE c.name = %s AND e.cmetadata->>'user_id' = %s
        LIMIT 1
    """
    try:
        with _get_pool().connection() as conn, conn.cursor() as cur:
            cur.execute(query, (pgvector_collection, user_id))
            return cur.fetchone() is not None
    except Exception as exc:
        raise RAGError(f"Failed to check document existence: {exc}") from exc


def extract_pdf_text(pdf_path: str) -> str:
    try:
        reader = PdfReader(pdf_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        raise RAGError(f"Failed to read PDF {pdf_path}: {exc}") from exc


def chunk_text(text: str, source: str, user_id: str) -> list[Document]:
    chunks = _splitter.split_text(text)
    return [
        Document(
            page_content=chunk,
            metadata={"source": source, "user_id": user_id, "chunk_index": i},
        )
        for i, chunk in enumerate(chunks)
    ]


def ingest_pdf(pdf_path: str, user_id: str, source_name: Optional[str] = None) -> int:
    """
    Extract, chunk, embed, and store a PDF, scoped to `user_id`.
    Returns the number of chunks stored. Synchronous / blocking — call this
    from a background task or via run_in_threadpool from async code, never
    directly in an async route handler.
    """
    text = extract_pdf_text(pdf_path)
    if not text.strip():
        logger.warning("No extractable text in %s", pdf_path)
        return 0

    docs = chunk_text(text, source=source_name or pdf_path, user_id=user_id)
    try:
        get_vectorstore().add_documents(docs)
    except Exception as exc:
        raise RAGError(f"Failed to store embeddings for {pdf_path}: {exc}") from exc
    return len(docs)


def search(query: str, user_id: str, top_k: Optional[int] = None) -> list[dict]:
    """
    Retrieve top-k chunks belonging to `user_id` only. Synchronous / blocking
    — wrap with run_in_threadpool when called from async code (see
    agents/nodes.py::retrieval_node).
    """
    k = top_k or top_k
    try:
        results = get_vectorstore().similarity_search_with_score(
            query, k=k, filter={"user_id": user_id}
        )
    except Exception as exc:
        raise RAGError(f"Retrieval failed: {exc}") from exc

    return [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "score": float(score),
            "metadata": doc.metadata,
        }
        for doc, score in results
    ]