"""
LangGraph node + routing functions for the medical agent.

All external calls (Groq STT, Groq LLM, pgvector search) are wrapped in
try/except so a provider failure becomes a graceful state["error"] +
fallback response instead of an unhandled exception bubbling out of the
graph. Blocking calls are wrapped in run_in_threadpool so they never stall
the event loop.
"""

import logging
from typing import Optional

from groq import Groq
from langchain_core.messages import AIMessage, BaseMessage
from starlette.concurrency import run_in_threadpool

from app.medical_agent.agents.prompts import (
    EMERGENCY_KEYWORDS,
    EMERGENCY_MESSAGE,
    SYSTEM_PROMPT,
    build_generation_prompt,
)
from app.medical_agent.agents.state import AgentState
from app.medical_agent.core.config import *
from app.medical_agent.services import rag_service, stt_service

logger = logging.getLogger(__name__)

_groq_client: Optional[Groq] = None

_ROLE_MAP = {"human": "user", "ai": "assistant", "system": "system"}


def _get_groq_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=llm_api_key)
    return _groq_client


def _to_groq_messages(messages: list[BaseMessage]) -> list[dict]:
    return [{"role": _ROLE_MAP.get(m.type, "user"), "content": m.content} for m in messages]


# ---- routing (conditional edges) --------------------------------------

def route_input(state: AgentState) -> str:
    return "stt" if state.get("input_mode") == "audio" else "safety_check"


def route_after_safety(state: AgentState) -> str:
    if state.get("is_emergency"):
        return "emergency_response"
    elif state.get("needs_retrieval", True):
        return "retrieval"
    else:
        return "generation"


# ---- nodes ---------------------------------------------------------------

async def stt_node(state: AgentState) -> AgentState:
    if not state.get("audio_path"):
        return {**state, "error": "input_mode is 'audio' but no audio_path was set."}
    try:
        transcript = await stt_service.transcribe_audio(state["audio_path"])
    except stt_service.STTError as exc:
        logger.exception("STT failed for session %s", state.get("session_id"))
        return {**state, "error": str(exc)}
    return {**state, "raw_query": transcript, "step_count": state.get("step_count", 0) + 1}


def safety_check_node(state: AgentState) -> AgentState:
    text = (state.get("raw_query") or "").lower()
    flags = [kw for kw in EMERGENCY_KEYWORDS if kw in text]
    return {
        **state,
        "is_emergency": bool(flags),
        "safety_flags": flags,
        "step_count": state.get("step_count", 0) + 1,
    }


def emergency_response_node(state: AgentState) -> AgentState:
    # No LLM call on purpose: static, predictable, zero added latency for
    # the path that most needs a fast, unambiguous answer.
    return {**state, "response": EMERGENCY_MESSAGE, "requires_disclaimer": True}


async def retrieval_node(state: AgentState) -> AgentState:
    if not state.get("needs_retrieval", True):
        return {**state, "documents_available": False, "retrieved_docs": [], "context": None}

    user_id = state.get("user_id") or "default"
    query = state.get("raw_query", "")

    try:
        docs = await run_in_threadpool(rag_service.search, query, user_id)
    except ValueError as exc:
        # Collection not found → no documents have been ingested yet
        logger.warning("No vector collection found, skipping retrieval: %s", exc)
        return {
            **state,
            "documents_available": False,
            "retrieved_docs": [],
            "context": None,
            "step_count": state.get("step_count", 0) + 1,
        }
    except rag_service.RAGError as exc:
        logger.exception("Retrieval failed for session %s", state.get("session_id"))
        return {
            **state,
            "error": str(exc),
            "documents_available": False,
            "retrieved_docs": [],
            "context": None,
        }

    context = "\n\n".join(f"[{d['source']}] {d['content']}" for d in docs) if docs else None
    return {
        **state,
        "documents_available": bool(docs),
        "retrieved_docs": docs,
        "context": context,
        "step_count": state.get("step_count", 0) + 1,
    }

async def generation_node(state: AgentState) -> AgentState:
    client = _get_groq_client()
    user_prompt = build_generation_prompt(
        state.get("raw_query", ""), state.get("context"), state.get("documents_available", False)
    )
    history = _to_groq_messages(state.get("messages", []))

    try:
        completion = await run_in_threadpool(
            lambda: client.chat.completions.create(
                model=llm_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *history,
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
        )
        answer = completion.choices[0].message.content
    except Exception as exc:
        logger.exception("Generation failed for session %s", state.get("session_id"))
        return {
            **state,
            "error": str(exc),
            "response": "Sorry, something went wrong generating a response. Please try again.",
        }

    citations = sorted({d["source"] for d in state.get("retrieved_docs", [])})
    return {
        **state,
        "response": answer,
        "citations": citations,
        "messages": [AIMessage(content=answer)],
        "requires_disclaimer": True,
        "step_count": state.get("step_count", 0) + 1,
    }