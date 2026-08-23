from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.medical_agent.db.models import User
from app.medical_agent.core.security import hash_password, verify_password, create_access_token
from app.medical_agent.schemas.user import UserCreate, UserLogin
from fastapi import HTTPException, status

async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(db: AsyncSession, login_data: UserLogin) -> User:
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

async def get_user_by_id(db: AsyncSession, user_id: str) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()