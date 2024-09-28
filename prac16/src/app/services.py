from typing import Annotated

from pydantic import EmailStr
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User as UserModel
from app.schemas import UserCreate, UserUpdateUsername, UserUpdateEmail
from fastapi import HTTPException, status, Depends

from core.database.session import provide_pg_session


class UserService:
    @staticmethod
    @provide_pg_session
    async def get_user_by_id(user_id: int, session: AsyncSession) -> UserModel:
        query = select(UserModel).filter(UserModel.id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    @staticmethod
    @provide_pg_session
    async def get_user_by_username(username: str, session: AsyncSession) -> UserModel:
        query = select(UserModel).filter(UserModel.username == username)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    @staticmethod
    @provide_pg_session
    async def get_user_by_email(email: EmailStr, session: AsyncSession) -> UserModel:
        query = select(UserModel).filter(UserModel.email == email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    @staticmethod
    @provide_pg_session
    async def create_user(user_data: UserCreate, session: AsyncSession) -> UserModel:
        new_user = UserModel(**user_data.model_dump())
        session.add(new_user)
        try:
            await session.commit()
            await session.refresh(new_user)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username or email already exists"
            )
        return new_user

    @staticmethod
    @provide_pg_session
    async def update_user_username(user_id: int, user_data: UserUpdateUsername, session: AsyncSession) -> UserModel:
        query = update(UserModel).where(UserModel.id == user_id).values(username=user_data.username)
        try:
            await session.execute(query)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        user = await UserService.get_user_by_id(user_id)
        return user

    @staticmethod
    @provide_pg_session
    async def update_user_email(user_id: int, user_data: UserUpdateEmail, session: AsyncSession) -> UserModel:
        query = update(UserModel).where(UserModel.id == user_id).values(email=user_data.email)
        try:
            await session.execute(query)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        user = await UserService.get_user_by_id(user_id)
        return user

    @staticmethod
    @provide_pg_session
    async def delete_user(user_id: int, session: AsyncSession) -> None:
        query = delete(UserModel).where(UserModel.id == user_id)
        await session.execute(query)
        await session.commit()

    @staticmethod
    @provide_pg_session
    async def verify_user(user_id: int, session: AsyncSession) -> UserModel:
        query = update(UserModel).where(UserModel.id == user_id).values(is_verified=True)
        await session.execute(query)
        await session.commit()
        user = await UserService.get_user_by_id(user_id)
        return user

