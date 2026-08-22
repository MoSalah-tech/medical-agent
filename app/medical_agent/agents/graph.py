"""
Builds the LangGraph graph, checkpointed to Postgres so conversation state
survives restarts and is shared correctly across multiple API
workers/replicas (a MemorySaver, in-process checkpointer, does NOT share
state across workers — every worker would see a different conversation).

Usage (wire into FastAPI's lifespan, once, at startup):

    from contextlib import asynccontextmanager
    from fastapi import FastAPI
    from medical_agent.agents.graph import get_compiled_graph

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with get_compiled_graph() as agent_graph:
            app.state.agent_graph = agent_graph
            yield

    app = FastAPI(lifespan=lifespan)

Then in a route:

    config = {"configurable": {"thread_id": session_id}}
    result = await request.app.state.agent_graph.ainvoke(state, config=config)
"""

from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.medical_agent.agents.nodes import (
    emergency_response_node,
    generation_node,
    retrieval_node,
    route_after_safety,
    route_input,
    safety_check_node,
    stt_node,
)
from app.medical_agent.agents.state import AgentState
from app.medical_agent.core.config import *


def _build_graph_skeleton() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("stt", stt_node)
    graph.add_node("safety_check", safety_check_node)
    graph.add_node("emergency_response", emergency_response_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("generation", generation_node)

    graph.set_conditional_entry_point(
        route_input, {"stt": "stt", "safety_check": "safety_check"}
    )
    graph.add_edge("stt", "safety_check")
    graph.add_conditional_edges(
    "safety_check",
    route_after_safety,
    {
        "emergency_response": "emergency_response",
        "retrieval": "retrieval",
        "generation": "generation",   
    },
)
    graph.add_edge("retrieval", "generation")
    graph.add_edge("generation", END)
    graph.add_edge("emergency_response", END)
    return graph


@asynccontextmanager
async def get_compiled_graph():
    """
    Async context manager — AsyncPostgresSaver owns a connection pool that
    needs to be opened once at startup and closed cleanly at shutdown, so
    this should be entered exactly once in your FastAPI lifespan, not per
    request.

    """ 
    async with AsyncPostgresSaver.from_conn_string(
         database_url_psycopg
     ) as checkpointer:
         await checkpointer.setup()  # idempotent; creates checkpoint tables on first run
         yield _build_graph_skeleton().compile(checkpointer=checkpointer)

# def get_compiled_graph():
#      """Return compiled graph with in-memory checkpointer."""
#      checkpointer = MemorySaver()
#      return _build_graph_skeleton().compile(checkpointer=checkpointer)
