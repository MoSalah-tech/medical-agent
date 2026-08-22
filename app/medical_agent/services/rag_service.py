from typing import Optional
from langchain_community.vectorstores import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app.medical_agent.core.config import (
    gemini_api_key,
    gemini_embedding_model,
    database_url_psycopg,
    pgvector_collection,
)
class RAGError(Exception):
    """Custom exception for RAG service errors."""
    pass



_embeddings = None
_vectorstore = None
_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = GoogleGenerativeAIEmbeddings(
            model=gemini_embedding_model,
            google_api_key=gemini_api_key,
        )
    return _embeddings

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore =  PGVector(
        embedding_function=get_embeddings(),
        collection_name=pgvector_collection,
        connection_string=database_url_psycopg,
        use_jsonb=False,
    )
    return _vectorstore

def extract_pdf_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

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
    text = extract_pdf_text(pdf_path)
    if not text.strip():
        return 0
    docs = chunk_text(text, source=source_name or pdf_path, user_id=user_id)
    get_vectorstore().add_documents(docs)
    return len(docs)

def search(query: str, user_id: str, top_k: int = 5) -> list[dict]:
    results = get_vectorstore().similarity_search_with_score(
        query, k = top_k if top_k is not None else 5, filter={"user_id": user_id}
    )
    return [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "score": float(score),
            "metadata": doc.metadata,
        }
        for doc, score in results
    ]