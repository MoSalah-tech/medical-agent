import os 
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import create_async_engine
from app.medical_agent.db.base import Base
from app.medical_agent.db.sessions import engine
from app.medical_agent.agents.graph import get_compiled_graph
from app.medical_agent.api.v1.router import api_router
from app.medical_agent.core.config import settings

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize agent graph with Postgres checkpointer
    app.state.agent_graph = None
    async with get_compiled_graph() as graph:
        app.state.agent_graph = graph
        yield
    await engine.dispose()

app = FastAPI(
    title="Medical Agent API",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}