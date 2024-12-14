from datetime import datetime
from typing import Literal, List
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

# # #

class WriterSchema(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True


class BookSchema(BaseModel):
    id: int
    title: str
    writers: List[WriterSchema]
    class Config:
        orm_mode = True


class PublisherSchema(BaseModel):
    id: int
    name: str
    books: List[BookSchema]
    class Config:
        orm_mode = True


class WriterCreate(BaseModel):
    name: str


class BookCreate(BaseModel):
    title: str
    writer_ids: List[int]


class PublisherCreate(BaseModel):
    name: str


class WriterUpdate(BaseModel):
    name: str


class BookUpdate(BaseModel):
    title: str
    writer_ids: List[int]


class PublisherUpdate(BaseModel):
    name: str

