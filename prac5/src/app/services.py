from pydantic import EmailStr

from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models import User as UserModel, Writer, Book, Publisher
from app.schemas import UserCreate, UserUpdateUsername, UserUpdateEmail, WriterCreate, WriterUpdate, BookCreate, \
    BookUpdate, PublisherCreate, PublisherUpdate
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

# # #

class WriterService:
    @staticmethod
    @provide_pg_session
    async def get_writer_by_id(writer_id: int, session: AsyncSession) -> Writer:
        query = select(Writer).where(Writer.id == writer_id)
        result = await session.execute(query)
        writer = result.scalar()
        if not writer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Writer not found")
        return writer

    @staticmethod
    @provide_pg_session
    async def create_writer(writer_data: WriterCreate, session: AsyncSession) -> Writer:
        new_writer = Writer(**writer_data.dict())
        session.add(new_writer)
        try:
            await session.commit()
            await session.refresh(new_writer)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Writer with this name already exists"
            )
        return new_writer

    @staticmethod
    @provide_pg_session
    async def update_writer(writer_id: int, writer_data: WriterUpdate, session: AsyncSession) -> Writer:
        query = update(Writer).where(Writer.id == writer_id).values(**writer_data.dict())
        await session.execute(query)
        await session.commit()
        writer = await WriterService.get_writer_by_id(writer_id, session)
        return writer

    @staticmethod
    @provide_pg_session
    async def delete_writer(writer_id: int, session: AsyncSession) -> None:
        query = delete(Writer).where(Writer.id == writer_id)
        await session.execute(query)
        await session.commit()

class BookService:
    @staticmethod
    @provide_pg_session
    async def get_book_by_id(book_id: int, session: AsyncSession) -> Book:
        query = select(Book).filter(Book.id == book_id)
        result = await session.execute(query)
        book = result.scalar_one_or_none()
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        return book

    @staticmethod
    @provide_pg_session
    async def create_book(book_data: BookCreate, session: AsyncSession) -> Book:
        new_book = Book(title=book_data.title)
        if book_data.writer_ids:
            writers_query = select(Writer).where(Writer.id.in_(book_data.writer_ids))
            writers_result = await session.execute(writers_query)
            new_book.writers = writers_result.scalars().all()
        session.add(new_book)
        try:
            await session.commit()
            await session.refresh(new_book)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book with this title already exists"
            )
        return new_book

    @staticmethod
    @provide_pg_session
    async def update_book(book_id: int, book_data: BookUpdate, session: AsyncSession) -> Book:
        query = update(Book).where(Book.id == book_id).values(title=book_data.title)
        await session.execute(query)
        if book_data.writer_ids:
            book = await BookService.get_book_by_id(book_id, session)
            writers_query = select(Writer).filter(Writer.id.in_(book_data.writer_ids))
            writers_result = await session.execute(writers_query)
            book.writers = writers_result.scalars().all()
        await session.commit()
        book = await BookService.get_book_by_id(book_id, session)
        return book

    @staticmethod
    @provide_pg_session
    async def delete_book(book_id: int, session: AsyncSession) -> None:
        query = delete(Book).where(Book.id == book_id)
        await session.execute(query)
        await session.commit()

class PublisherService:
    @staticmethod
    @provide_pg_session
    async def get_publisher_by_id(publisher_id: int, session: AsyncSession) -> Publisher:
        query = select(Publisher).filter(Publisher.id == publisher_id)
        result = await session.execute(query)
        publisher = result.scalar_one_or_none()
        if not publisher:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publisher not found")
        return publisher

    @staticmethod
    @provide_pg_session
    async def create_publisher(publisher_data: PublisherCreate, session: AsyncSession) -> Publisher:
        new_publisher = Publisher(**publisher_data.dict())
        session.add(new_publisher)
        try:
            await session.commit()
            await session.refresh(new_publisher)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Publisher with this name already exists"
            )
        return new_publisher

    @staticmethod
    @provide_pg_session
    async def update_publisher(publisher_id: int, publisher_data: PublisherUpdate, session: AsyncSession) -> Publisher:
        query = update(Publisher).where(Publisher.id == publisher_id).values(**publisher_data.dict())
        await session.execute(query)
        await session.commit()
        publisher = await PublisherService.get_publisher_by_id(publisher_id, session)
        return publisher

    @staticmethod
    @provide_pg_session
    async def delete_publisher(publisher_id: int, session: AsyncSession) -> None:
        query = delete(Publisher).where(Publisher.id == publisher_id)
        await session.execute(query)
        await session.commit()

