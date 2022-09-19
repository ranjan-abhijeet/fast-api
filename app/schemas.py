from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserEmail(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    email: EmailStr
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PostBase(BaseModel):
    title: str
    content: str
    publish: bool = True


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    post_id: int
    created_at: datetime
    owner: UserEmail

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
