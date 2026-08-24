import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.medical_agent.db.sessions import get_db
from app.medical_agent.api.dependencies import get_current_user
from app.medical_agent.db.models import User
from app.medical_agent.services.rag_service import ingest_file
from app.medical_agent.schemas.file import FileUploadResponse
from app.medical_agent.core.config import settings  # if you have UPLOAD_DIR here

router = APIRouter()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    allowed_extensions = {".pdf", ".docx", ".txt", ".text", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(400, f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}")

    # Save to uploads/ directory with unique name
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_id = str(uuid.uuid4())
    dest_path = upload_dir / f"{file_id}{ext}"

    with open(dest_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    try:
        chunks = ingest_file(str(dest_path), user_id=str(current_user.id), source_name=file.filename)
    except Exception as e:
        # Optionally keep the file for debugging? But delete to avoid clutter
        if dest_path.exists():
            dest_path.unlink()
        raise HTTPException(500, f"Ingestion failed: {str(e)}")

    # Delete the file after successful ingestion
    if dest_path.exists():
        dest_path.unlink()

    return FileUploadResponse(message="File processed successfully", chunks_ingested=chunks)