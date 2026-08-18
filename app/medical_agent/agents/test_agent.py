import asyncio
from dotenv import load_dotenv

# Load .env (including LangSmith vars)
load_dotenv()

# Ensure LangSmith is enabled (optional if .env already set)
import os
if os.getenv("LANGSMITH_TRACING") != "true":
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = "your_langsmith_api_key"   # replace
    os.environ["LANGSMITH_PROJECT"] = "medical-agent"
    os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"

from app.medical_agent.agents.graph import get_compiled_graph
from app.medical_agent.agents.state import new_state

async def main():
    # If get_compiled_graph is an async context manager (Postgres saver)
    # async with get_compiled_graph() as graph:
    #     ... (see below)

    # If get_compiled_graph returns a compiled graph directly (MemorySaver)
    graph = get_compiled_graph()

    # Build initial state using your factory function
    state = new_state(
        query="I have a headache and fever",
        session_id="test-session-001",
        user_id="test-user-001",
        input_mode="text",
    )

    # Config for checkpointing (thread_id = conversation)
    config = {"configurable": {"thread_id": "test-thread-001"}}

    print("Invoking agent...")
    result = await graph.ainvoke(state, config=config)

    # Print the final response
    print("\n--- Agent Response ---")
    print(result.get("response", "No response field"))

    print("\n--- Safety Flags ---")
    print(result.get("safety_flags", []))
    print("Emergency?", result.get("is_emergency", False))

    print("\n--- Retrieved Docs (if any) ---")
    for doc in result.get("retrieved_docs", []):
        print(f"- {doc.get('source', 'unknown')}: {doc.get('content', '')[:80]}...")

if __name__ == "__main__":
    asyncio.run(main())