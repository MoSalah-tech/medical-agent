from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class ConversationOut(BaseModel):
    id: UUID
    session_id: str
    title: str | None
    created_at: datetime
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)