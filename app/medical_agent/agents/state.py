"""
AgentState: the single shared state object that flows through every node
of the LangGraph graph.
"""

from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class RetrievedDoc(TypedDict):
    content: str
    source: str
    score: float
    metadata: Dict[str, Any]


class AgentState(TypedDict):
    # ---- conversation / identity -----------------------------------------
    messages: Annotated[List[BaseMessage], add_messages]
    session_id: str
    user_id: Optional[str]
    web_results:List[dict]

    # ---- input handling -----------------------------------------------
    input_mode: Literal["text", "audio"]
    audio_path: Optional[str]
    raw_query: Optional[str]

    # ---- safety / triage -------------------------------------------------
    is_emergency: bool
    is_medical: bool
    safety_flags: List[str]
    requires_disclaimer: bool

    # ---- retrieval (RAG) -------------------------------------------------
    # RAG is optional: most turns will have no uploaded documents at all,
    # and the agent should behave like a normal chat in that case.
    needs_retrieval: bool          # set False to skip retrieval entirely (e.g. greetings)
    documents_available: bool      # True only if this user has ever uploaded something
    retrieved_docs: List[RetrievedDoc]
    context: Optional[str]

    # ---- generation --------------------------------------------------
    response: Optional[str]
    citations: List[str]

    # ---- control / debugging -------------------------------------------
    error: Optional[str]
    step_count: int


def new_state(
    query: str,
    session_id: str,
    user_id: str,
    input_mode: Literal["text", "audio"] = "text",
    audio_path: Optional[str] = None,
) -> AgentState:
    return AgentState(
        messages=[],
        session_id=session_id,
        user_id=user_id,
        input_mode=input_mode,
        audio_path=audio_path,
        raw_query=query,
        is_emergency=False,
        is_medical=True,
        safety_flags=[],
        requires_disclaimer=False,
        needs_retrieval=True,
        documents_available=False,
        web_results=[],
        retrieved_docs=[],
        context=None,
        response=None,
        citations=[],
        error=None,
        step_count=0,
    )