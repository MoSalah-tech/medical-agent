# Medical Agent API

An AI-powered medical assistant built with **FastAPI**, **LangGraph**, and **pgvector**. It supports **text chat**, **voice input (STT)**, **PDF upload for RAG**, and **JWT authentication**. The system uses a multi-step agent graph to check for emergencies, retrieve relevant personal health documents, and generate safe, grounded medical information.

> ⚠️ **Disclaimer:** This project is for educational and informational purposes only. It does not provide medical diagnosis or treatment. Always consult a licensed healthcare professional.

---

## Features

- **Multi-modal Input**:  
  - Text chat via REST API  
  - Audio input (speech-to-text)  
  - PDF document upload for personalized RAG

- **Medical Safety Guard**:  
  - Emergency keyword detection (chest pain, suicidal, etc.)  
  - Always appends a medical disclaimer

- **Retrieval-Augmented Generation (RAG)**:  
  - Ingest medical PDFs (lab results, visit notes)  
  - Store embeddings in Supabase using `pgvector`  
  - Retrieve relevant chunks per user during conversations

- **JWT Authentication**:  
  - User registration & login  
  - Protected endpoints

- **Conversation Memory**:  
  - LangGraph checkpointing with PostgreSQL (persists across restarts)  
  - Thread-based conversation state

- **Rate Limiting**:  
  - Endpoint-level limits using `slowapi`

- **LangSmith Tracing**:  
  - Optional integration for debugging and monitoring

---

## Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Agent Orchestration**: LangGraph
- **LLM**: Groq (Llama 3.3 70B, GPT-OSS-120B) or Google Gemini
- **Embeddings**: Gemini (gemini-embedding-001)
- **Speech-to-Text**: Groq Whisper
- **Vector Store**: pgvector (via `langchain-community` PGVector)
- **Database**: PostgreSQL (Supabase) with SQLAlchemy async & pgvector
- **Auth**: JWT (`python-jose`), password hashing (`passlib[bcrypt]`)
- **Rate Limiting**: slowapi
- **Tracing**: LangSmith (optional)

---

The agent uses a **checkpointed state graph** to remember conversation context and ensure safe routing.



---

## Setup Instructions

### 1. Clone the Repository
Using uv (recommended):

```bash
git clone https://github.com/MoSalah-tech/medical-agent.git
cd medical-agent
```
### 2.  Create Virtual Environment

```bash
uv venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```
Or with standard venv:
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
With uv:
```bash
uv pip install -r requirements.txt
```

Or with pip:
```bash
pip install -r requirements.txt
```
### 4. Set Up Environment Variables
Copy .env.example to .env and fill in the values:

**Note** DATABASE_URL_ASYNC must use +asyncpg driver. DATABASE_URL_PSYCOPG is for LangGraph checkpointer and pgvector.

### 5.  Database Setup (Supabase)

-Create a Supabase project.
-Enable the vector extension.
-Run the SQL script to create the necessary tables (or let the app create them automatically for app tables, but for checkpoint tables, the app will create them via AsyncPostgresSaver.setup()).


If you want to create the vector tables manually, run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The application will create langchain_pg_embedding and langchain_pg_collection when you first upload a document.

### 6. Run the Server
```bash
uvicorn app.medical_agent.main:app --reload
```

The server will start at http://127.0.0.1:8000.

## API Endpoints

### Health Check

- `GET /health`

### Authentication

- `POST /api/v1/auth/register`

  Request body:
  ```json
  {
    "email": "user@example.com",
    "password": "secure123",
    "full_name": "John Doe"
  }
  ```

- `POST /api/v1/auth/login`

  Form data: `username` (email), `password`
  Returns JWT token.

### Chat

- `POST /api/v1/chat`

  Requires `Authorization: Bearer <token>` header.

  Body:
  ```json
  {
    "text": "I have a headache and fever",
    "session_id": null
  }
  ```

### Voice Input

- `POST /api/v1/voice`

  Requires `Authorization` header.

  `multipart/form-data` with:
  - `audio`: audio file
  - `session_id`: (optional)

### File Upload (RAG)

- `POST /api/v1/files/upload`

  Requires `Authorization` header.

  `multipart/form-data` with:
  - `file`: PDF file
    





