"""
Application settings, loaded and validated from .env at import time.

Using pydantic-settings (not a plain class) means a missing required key
fails immediately at startup with a clear message, instead of silently
becoming "" and failing later as a confusing 401 from Groq/Gemini.
"""
import os 
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file

llm_api_key = os.getenv("GROQ_API_KEY")
llm_model = os.getenv("GROQ_LLM_MODEL", "openai/gpt-oss-120b")
llm_provider = os.getenv("LLM_PROVIDER", "groq")
gemini_api_key = os.getenv("GEMINI_API_KEY")
embedding_provider = os.getenv("EMBEDDING_PROVIDER", "gemini")
gemini_embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
groq_stt_model = os.getenv("GROQ_STT_MODEL", "whisper-large-v3")
database_url = os.getenv("DATABASE_URL")
database_url_psycopg = os.getenv("DATABASE_URL_PSYCOPG")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")


pgvector_collection = os.getenv("PGVECTOR_COLLECTION", "medical_documents")
top_k = int(os.getenv("RETRIEVAL_TOP_K", 5))


os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "medical-agent")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.langsmith.com")

print("Tracing:", os.environ.get("LANGSMITH_TRACING", "false"))
print("Project:", os.environ["LANGSMITH_PROJECT"])










# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     model_config = SettingsConfigDict(env_file=".env", extra="ignore")

#     # ---- Database ----------------------------------------------------
#     # App data (users, conversations, messages) via SQLAlchemy's async engine.
#     DATABASE_URL: str  # postgresql+asyncpg://user:pass@host:5432/db

#     # Same Postgres instance, psycopg-style DSN. Used by pgvector and the
#     # LangGraph checkpointer — neither speaks the asyncpg driver.
#     DATABASE_URL_PSYCOPG: str  # postgresql://user:pass@host:5432/db

#     #--- LangSmith ----------------------------------------------------
#     LANGSMITH_TRACING: str
#     LANGSMITH_API_KEY: str  # LangSmith API key for logging LLM calls
#     LANGSMITH_ENDPOINT: str
#     LANGSMITH_PROJECT: str
#     # ---- API keys ------------------------------------------------------
#     GROQ_API_KEY: str
#     GEMINI_API_KEY: str

#     # ---- LLM -----------------------------------------------------------
#     LLM_PROVIDER: str = "groq"
#     GROQ_LLM_MODEL: str = "openai/gpt-oss-120b"
#     GEMINI_LLM_MODEL: str = "gemini-1.5-flash"

#     # ---- Embeddings ------------------------------------------------------
#     EMBEDDING_PROVIDER: str = "gemini"
#     GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"

#     # ---- STT -------------------------------------------------------------
#     GROQ_STT_MODEL: str = "whisper-large-v3"

#     # ---- Vector store (pgvector) ------------------------------------------
#     PGVECTOR_COLLECTION: str = "medical_documents"
#     RETRIEVAL_TOP_K: int = 5


# settings = Settings()