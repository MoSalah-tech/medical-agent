from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.medical_agent.db.sessions import get_db
from app.medical_agent.schemas.user import UserCreate, UserLogin, Token, UserOut
from app.medical_agent.services import user_service
from app.medical_agent.core.security import create_access_token
from datetime import timedelta
from app.medical_agent.core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await user_service.create_user(db, user_data)
    return user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await user_service.authenticate_user(db, UserLogin(email=form_data.username, password=form_data.password))
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}