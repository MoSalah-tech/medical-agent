import uuid
from fastapi import APIRouter, Depends, Request,HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.medical_agent.core.security import decode_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.medical_agent.db.sessions import get_db
from app.medical_agent.schemas.chat import ChatRequest, ChatResponse
from app.medical_agent.services.chat_service import process_text_message, list_conversations, delete_conversation
from app.medical_agent.api.dependencies import get_current_user, limiter
from app.medical_agent.db.models import User , Conversation, Message
from app.medical_agent.schemas.conversation import ConversationOut


router = APIRouter()

@router.post("", response_model=ChatResponse)
@limiter.limit("100/minute")
async def chat(
    request: Request,
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    graph = request.app.state.agent_graph
    return await process_text_message(db, str(current_user.id), req.text, req.session_id, graph)




@router.get("/conversations", response_model=list[ConversationOut])
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    convs = await list_conversations(db, str(current_user.id))
    return convs


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: uuid.UUID,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    # Decode token to get user_id
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Check if conversation exists and belongs to user
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Delete messages and conversation
    await db.execute(delete(Message).where(Message.conversation_id == conversation_id))
    await db.execute(delete(Conversation).where(Conversation.id == conversation_id))
    await db.commit()

    return {"message": "Conversation deleted"}


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: uuid.UUID,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    conv = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    )
    conversation = conv.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msgs = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
    )
    messages = msgs.scalars().all()

    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]