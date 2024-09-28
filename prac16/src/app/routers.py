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


@auth_router.post("/me/verify")
async def verify_new_user(email: EmailStr, code: int):
    user = await Users.get_user_by_email(email)
    await Codes.verify(user.id, code, "new_user_verify")
    user = await Users.verify_user(user.id)
    response = JSONResponse(UserSchema(**user.to_dict()).model_dump())
    response.set_cookie("access", create_jwt_token(user.id, "access"))
    return response
