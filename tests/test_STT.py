 # generate_test_audio.py
import os
import asyncio
from dotenv import load_dotenv
from app.medical_agent.agents.graph import get_compiled_graph
from app.medical_agent.agents.state import new_state


if os.getenv("LANGSMITH_TRACING") != "true":
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = "ylsv2_pt_c4eff0de8ef84d6eaf75f0292a8cbe2e_ac7ce7276a"
    os.environ["LANGSMITH_PROJECT"] = "medical-agent"
    os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"






async def main():
    graph = get_compiled_graph()

    state = new_state(
        query="",                # raw_query can be empty; STT will fill it
        session_id="test-audio-session-001",
        user_id="test-user-001",
        input_mode="audio",
        audio_path="data/audio/test_audio.mp3",   # path to your audio file
    )

    config = {"configurable": {"thread_id": "test-audio-thread-001"}}

    print("Invoking agent with audio...")
    result = await graph.ainvoke(state, config=config)

    print("\n--- Transcribed Text ---")
    print(result.get("raw_query") or "No raw_query field")

    print("\n--- Agent Response ---")
    print(result.get("response", "No response field"))

if __name__ == "__main__":
    asyncio.run(main())


