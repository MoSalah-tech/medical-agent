from fastapi import APIRouter
from app.medical_agent.api.v1.endpoints import auth, chat, voice, files

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(files.router, prefix="/files", tags=["files"])