from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import EmailStr
from starlette.responses import Response, JSONResponse

from app.depends import get_active_user
from app.models import User as UserModel
from app.schemas import User as UserSchema, UserUpdateUsername, UserUpdateEmail, UserCreate
from app.services import UserService as Users
from core.security.codes import Codes
from core.security.tokens import create_jwt_token
from worker.tasks import send_user_verify_message

ActiveUserDep = Annotated[UserModel, Depends(get_active_user)]
user_router = APIRouter(prefix="/user", tags=["User"])
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@user_router.get("/me")
async def get_user_me(me: ActiveUserDep):
    return UserSchema(**me.to_dict())


@user_router.post("/me")
async def create_user_me(user_data: UserCreate):
    new_user = await Users.create_user(user_data)
    code = await Codes.generate(new_user.id, "new_user_verify")
    send_user_verify_message.delay(new_user.email, code)
    return Response(status_code=status.HTTP_201_CREATED)


@user_router.patch("/me/username")
async def update_username_me(me: ActiveUserDep, user_data: UserUpdateUsername):
    me = await Users.update_user_username(me.id, user_data)
    return UserSchema(**me.to_dict())


@user_router.patch("/me/email", include_in_schema=False)
async def update_email_me(me: ActiveUserDep, user_data: UserUpdateEmail):
    ...


@user_router.get("/{user_id}")
async def get_user(_: ActiveUserDep, user_id: int):
    user = await Users.get_user_by_id(user_id)
    return UserSchema(**user.to_dict())


@auth_router.post("/verify/new")
async def verify_new_user(email: EmailStr, code: int):
    user = await Users.get_user_by_email(email)
    await Codes.verify(user.id, code, "new_user_verify")
    user = await Users.verify_user(user.id)
    response = JSONResponse(UserSchema(**user.to_dict()).model_dump())
    response.set_cookie("access", create_jwt_token(user.id, "access"))
    return response


@auth_router.post("/send-login")
async def request_login_user(email: EmailStr):
    user = await Users.get_user_by_email(email)
    code = await Codes.generate(user.id, "old_user_login")
    send_user_verify_message.delay(email, code)
    return Response(status_code=status.HTTP_201_CREATED)


@auth_router.post("/verify/me")
async def check_user_login(email: EmailStr, code: int):
    user = await Users.get_user_by_email(email)
    await Codes.verify(user.id, code, "old_user_login")
    response = JSONResponse(UserSchema(**user.to_dict()).model_dump())
    response.set_cookie("access", create_jwt_token(user.id, "access"))
    return response


from fastapi import APIRouter, Depends, status
from starlette.responses import Response, JSONResponse

from app.schemas import (
    WriterSchema,
    WriterCreate,
    WriterUpdate,
    BookSchema,
    BookCreate,
    BookUpdate,
    PublisherSchema,
    PublisherCreate,
    PublisherUpdate,
)
from app.services import WriterService, BookService, PublisherService

writer_router = APIRouter(prefix="/writers", tags=["Writers"])
book_router = APIRouter(prefix="/books", tags=["Books"])
publisher_router = APIRouter(prefix="/publishers", tags=["Publishers"])

# Writer Routes
@writer_router.get("/{writer_id}", response_model=WriterSchema)
async def get_writer(writer_id: int):
    writer = await WriterService.get_writer_by_id(writer_id)
    return writer

@writer_router.post("/", response_model=WriterSchema, status_code=status.HTTP_201_CREATED)
async def create_writer(writer_data: WriterCreate):
    writer = await WriterService.create_writer(writer_data)
    return writer

@writer_router.put("/{writer_id}", response_model=WriterSchema)
async def update_writer(writer_id: int, writer_data: WriterUpdate):
    writer = await WriterService.update_writer(writer_id, writer_data)
    return writer

@writer_router.delete("/{writer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_writer(writer_id: int):
    await WriterService.delete_writer(writer_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Book Routes
@book_router.get("/{book_id}", response_model=BookSchema)
async def get_book(book_id: int):
    book = await BookService.get_book_by_id(book_id)
    return book

@book_router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(book_data: BookCreate):
    book = await BookService.create_book(book_data)
    return book

@book_router.put("/{book_id}", response_model=BookSchema)
async def update_book(book_id: int, book_data: BookUpdate):
    book = await BookService.update_book(book_id, book_data)
    return book

@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    await BookService.delete_book(book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Publisher Routes
@publisher_router.get("/{publisher_id}", response_model=PublisherSchema)
async def get_publisher(publisher_id: int):
    publisher = await PublisherService.get_publisher_by_id(publisher_id)
    return publisher

@publisher_router.post("/", response_model=PublisherSchema, status_code=status.HTTP_201_CREATED)
async def create_publisher(publisher_data: PublisherCreate):
    publisher = await PublisherService.create_publisher(publisher_data)
    return publisher

@publisher_router.put("/{publisher_id}", response_model=PublisherSchema)
async def update_publisher(publisher_id: int, publisher_data: PublisherUpdate):
    publisher = await PublisherService.update_publisher(publisher_id, publisher_data)
    return publisher

@publisher_router.delete("/{publisher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_publisher(publisher_id: int):
    await PublisherService.delete_publisher(publisher_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
