from typing import Literal, Annotated, Optional

from fastapi.security import APIKeyCookie
from fastapi import Depends, HTTPException, status

from core.security.tokens import verify_jwt_token
from app.schemas import TokenData
from app.services import UserService as Users

access_token_scheme = APIKeyCookie(
    name="access",
    scheme_name="Cookie access token",
    description="Не трогай если не знаешь зачем это.",
    auto_error=True,
)
refresh_token_scheme = APIKeyCookie(
    name="refresh",
    scheme_name="Cookie refresh token",
    description="Не трогай если не знаешь зачем это.",
    auto_error=True,
)

token_mapper: dict[Literal["access", "refresh"], APIKeyCookie] = {
    "access": access_token_scheme,
    "refresh": refresh_token_scheme
}

def get_token(context: Literal["access", "refresh"], need_raise: bool = True):
    def wrapper(token=Depends(token_mapper[context])) -> Optional[TokenData]:
        try:
            return verify_jwt_token(token, context)
        except HTTPException as e:
            if need_raise:
                raise e

            return None

    return wrapper


async def get_active_user(token: Annotated[TokenData, Depends(get_token("access"))]):
    if (current_user := await Users.get_user_by_id(token.user_id)).is_verified:
        return current_user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not active")

