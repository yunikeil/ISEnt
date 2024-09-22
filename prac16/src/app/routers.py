from fastapi import APIRouter, Depends

from app import schemas as sh

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("/me")
async def get_me(user: sh.User = Depends()):
    return {"user_id": "ю"}


@user_router.get("/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}





auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/test")
async def test():
    return {"message": "Hello World"}
