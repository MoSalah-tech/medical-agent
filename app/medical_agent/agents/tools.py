"""
LangChain tool wrappers around the underlying services.

Not wired into the graph today — the current graph is a fixed
retrieve-then-generate pipeline (see graph.py), which is the right choice
for a predictable, auditable medical flow. This file exists for when/if you
want the LLM itself to decide whether to search documents (a tool-calling
agent instead of a fixed graph edge) — the tools are ready to bind to the
model at that point.
"""

from langchain_core.tools import tool

from medical_agent.services import rag_service


@tool
def search_medical_documents(query: str, user_id: str) -> str:
    """Search the user's uploaded medical documents for passages relevant
    to the query. Returns the top matches with their source filenames."""
    results = rag_service.search(query, user_id=user_id)
    if not results:
        return "No relevant documents found."
    return "\n\n".join(f"[{r['source']}] {r['content']}" for r in results)