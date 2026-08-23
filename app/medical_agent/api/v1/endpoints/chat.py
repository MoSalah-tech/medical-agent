from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.medical_agent.db.sessions import get_db
from app.medical_agent.schemas.chat import ChatRequest, ChatResponse
from app.medical_agent.services.chat_service import process_text_message
from app.medical_agent.api.dependencies import get_current_user, limiter
from app.medical_agent.db.models import User

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