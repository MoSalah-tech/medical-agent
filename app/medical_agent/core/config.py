"""
Application settings, loaded and validated from .env at import time.

Using pydantic-settings (not a plain class) means a missing required key
fails immediately at startup with a clear message, instead of silently
becoming "" and failing later as a confusing 401 from Groq/Gemini.
"""

# from dotenv import load_dotenv


# load_dotenv()  # Load environment variables from .env file

# llm_api_key = os.getenv("GROQ_API_KEY")
# llm_model = os.getenv("GROQ_LLM_MODEL", "openai/gpt-oss-120b")
# llm_provider = os.getenv("LLM_PROVIDER", "groq")
# gemini_api_key = os.getenv("GEMINI_API_KEY")
# embedding_provider = os.getenv("EMBEDDING_PROVIDER", "gemini")
# gemini_embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
# groq_stt_model = os.getenv("GROQ_STT_MODEL", "whisper-large-v3")
# database_url = os.getenv("DATABASE_URL")
# database_url_psycopg = os.getenv("DATABASE_URL_PSYCOPG")
# langsmith_api_key = os.getenv("LANGSMITH_API_KEY")


# pgvector_collection = os.getenv("PGVECTOR_COLLECTION", "medical_documents")
# top_k = int(os.getenv("RETRIEVAL_TOP_K", 5))


# os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "medical-agent")
# os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.langsmith.com")

# print("Tracing:", os.environ.get("LANGSMITH_TRACING", "false"))
# print("Project:", os.environ["LANGSMITH_PROJECT"])


import os 
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    UPLOAD_DIR: str = "uploads"  # Directory to store uploaded files
    # Required fields
    GROQ_API_KEY: str
    GEMINI_API_KEY: str
    DATABASE_URL_PSYCOPG: str
    DATABASE_URL_ASYNC: str        # <-- add this
    TAVILY_API_KEY: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Optional with defaults
    LLM_PROVIDER: str = "groq"
    GROQ_LLM_MODEL: str = "openai/gpt-oss-120b"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_PROVIDER: str = "gemini"
    GROQ_STT_MODEL: str = "whisper-large-v3"
    PGVECTOR_COLLECTION: str = "medical_documents"
    RETRIEVAL_TOP_K: int = 5
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    LANGSMITH_TRACING: str = "false"
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_PROJECT: str = "medical-agent"


settings = Settings()

# ---- Module-level aliases (backward compatibility) ----
# Many modules still use `from app.medical_agent.core.config import *`
# or import names like `database_url_psycopg`, `gemini_api_key`, etc.
GROQ_API_KEY = settings.GROQ_API_KEY
GEMINI_API_KEY = settings.GEMINI_API_KEY
DATABASE_URL_PSYCOPG = settings.DATABASE_URL_PSYCOPG
DATABASE_URL_ASYNC = settings.DATABASE_URL_ASYNC
SECRET_KEY = settings.SECRET_KEY
LLM_PROVIDER = settings.LLM_PROVIDER
GROQ_LLM_MODEL = settings.GROQ_LLM_MODEL
EMBEDDING_PROVIDER = settings.EMBEDDING_PROVIDER  # may not exist; skip if not used
GEMINI_EMBEDDING_MODEL = settings.GEMINI_EMBEDDING_MODEL
GROQ_STT_MODEL = settings.GROQ_STT_MODEL
PGVECTOR_COLLECTION = settings.PGVECTOR_COLLECTION
RETRIEVAL_TOP_K = settings.RETRIEVAL_TOP_K
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
RATE_LIMIT_REQUESTS = settings.RATE_LIMIT_REQUESTS
RATE_LIMIT_PERIOD = settings.RATE_LIMIT_PERIOD
LANGSMITH_TRACING = settings.LANGSMITH_TRACING
LANGSMITH_API_KEY = settings.LANGSMITH_API_KEY
LANGSMITH_ENDPOINT = settings.LANGSMITH_ENDPOINT
LANGSMITH_PROJECT = settings.LANGSMITH_PROJECT

# For convenience
llm_api_key = settings.GROQ_API_KEY
llm_model = settings.GROQ_LLM_MODEL
gemini_api_key = settings.GEMINI_API_KEY
gemini_embedding_model = settings.GEMINI_EMBEDDING_MODEL
groq_stt_model = settings.GROQ_STT_MODEL
database_url = settings.DATABASE_URL_ASYNC  # alias for old name
database_url_psycopg = settings.DATABASE_URL_PSYCOPG
pgvector_collection = settings.PGVECTOR_COLLECTION
top_k = settings.RETRIEVAL_TOP_K
langsmith_api_key = settings.LANGSMITH_API_KEY