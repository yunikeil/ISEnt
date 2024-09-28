from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_verified: bool


class UserCreate(BaseModel):
    username: str
    email: EmailStr


class UserUpdateUsername(BaseModel):
    username: str


class UserUpdateEmail(BaseModel):
    email: EmailStr


class UserSelfDelete(BaseModel):
    pass


class TokenData(BaseModel):
    user_id: int
    token_type: Literal["access", "refresh"]
    exp: datetime
    session: UUID
