import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.medical_agent.db.models import Conversation
from app.medical_agent.db.models import Message
from app.medical_agent.agents.state import new_state
from app.medical_agent.schemas.chat import ChatResponse

async def process_text_message(
    db: AsyncSession,
    user_id: str,
    text: str,
    session_id: Optional[str],
    graph
) -> ChatResponse:
    # Determine thread_id
    if session_id:
        thread_id = session_id
    else:
        thread_id = str(uuid.uuid4())

    # Ensure a conversation row exists for this user + thread_id
    result = await db.execute(
        select(Conversation).where(
            Conversation.session_id == thread_id,
            Conversation.user_id == user_id,
        )
    )
    conversation = result.scalar_one_or_none()

    if conversation is None:
        # Create new conversation
        conversation = Conversation(user_id=user_id, session_id=thread_id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # Build initial state for the agent
    state = new_state(
        query=text,
        session_id=thread_id,
        user_id=user_id,
        input_mode="text",
    )
    config = {"configurable": {"thread_id": thread_id}}

    # Invoke the agent graph
    agent_result = await graph.ainvoke(state, config=config)

    # Save user and assistant messages using conversation.id
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=text,
    )
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=agent_result.get("response", ""),
    )
    db.add_all([user_msg, assistant_msg])
    await db.commit()

    return ChatResponse(
        response=agent_result.get("response", "No response"),
        citations=agent_result.get("citations", []),
        conversation_id=thread_id,
    )