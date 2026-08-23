from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    text: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    citations: List[str] = []
    conversation_id: Optional[str] = None