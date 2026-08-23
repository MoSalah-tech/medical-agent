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

## Architecture
