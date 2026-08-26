import os
import tempfile
from fastapi import APIRouter, Depends, Request, UploadFile, File
from fastapi import Form 
from sqlalchemy.ext.asyncio import AsyncSession
from app.medical_agent.db.sessions import get_db
from app.medical_agent.schemas.chat import ChatResponse
from app.medical_agent.services.stt_service import transcribe_audio
from app.medical_agent.services.chat_service import process_text_message
from app.medical_agent.api.dependencies import get_current_user, limiter
from app.medical_agent.db.models import User

router = APIRouter()

@router.post("", response_model=ChatResponse)
@limiter.limit("50/minute")
 

async def voice_input(
    request: Request,
    audio: UploadFile = File(...),
    session_id: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    suffix = os.path.splitext(audio.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        transcript = await transcribe_audio(tmp_path)
    finally:
        os.unlink(tmp_path)
    graph = request.app.state.agent_graph
    return await process_text_message(db, str(current_user.id), transcript, session_id, graph)