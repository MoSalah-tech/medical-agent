import os
import tempfile
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.medical_agent.db.sessions import get_db
from app.medical_agent.api.dependencies import get_current_user
from app.medical_agent.db.models import User
from app.medical_agent.services.rag_service import ingest_pdf
from app.medical_agent.schemas.file import FileUploadResponse

router = APIRouter()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        chunks = ingest_pdf(tmp_path, user_id=str(current_user.id), source_name=file.filename)
    except Exception as e:
        raise HTTPException(500, f"Ingestion failed: {str(e)}")
    finally:
        os.unlink(tmp_path)

    return FileUploadResponse(message="File processed successfully", chunks_ingested=chunks)