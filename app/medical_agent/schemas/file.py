from pydantic import BaseModel
from typing import Optional

class FileUploadResponse(BaseModel):
    message: str
    chunks_ingested: int