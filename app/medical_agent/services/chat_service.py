import uuid
from typing import Optional
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
    # Create or get conversation
    if session_id:
        # Use existing thread_id
        thread_id = session_id
    else:
        thread_id = str(uuid.uuid4())
        # Create conversation in DB
        conv = Conversation(user_id=user_id, session_id=thread_id)
        db.add(conv)
        await db.commit()

    # Build initial state
    state = new_state(
        query=text,
        session_id=thread_id,
        user_id=user_id,
        input_mode="text",
    )

    config = {"configurable": {"thread_id": thread_id}}

    # Invoke graph
    result = await graph.ainvoke(state, config=config)

    # Save user message and assistant response to DB
    user_msg = Message(conversation_id=(await _get_conversation_id(db, thread_id)), role="user", content=text)
    assistant_msg = Message(conversation_id=(await _get_conversation_id(db, thread_id)), role="assistant", content=result.get("response", ""))
    db.add(user_msg)
    db.add(assistant_msg)
    await db.commit()

    return ChatResponse(
        response=result.get("response", "No response"),
        citations=result.get("citations", []),
        conversation_id=thread_id,
    )

async def _get_conversation_id(db: AsyncSession, session_id: str) -> str:
    from sqlalchemy import select
    from app.medical_agent.db.models import Conversation
    res = await db.execute(select(Conversation.id).where(Conversation.session_id == session_id))
    return res.scalar_one()