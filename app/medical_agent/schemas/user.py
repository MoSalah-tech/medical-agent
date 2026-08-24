from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

import uuid
from pydantic import BaseModel, EmailStr, ConfigDict

class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str = None
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"