import uuid
from datetime import datetime, timedelta
from typing import Literal

from jose import jwt, JWTError
from fastapi.exceptions import HTTPException

from app.schemas import TokenData


def create_jwt_token(
        user_id: int,
        token_type: Literal["email", "access", "refresh"],
        secret: str = "super_secret",  # NOT GOOD
        expires_delta: timedelta | float = 0.5,
) -> str:
    if isinstance(expires_delta, float):
        expires_delta = timedelta(minutes=expires_delta)

    to_encode = {
        "user_id": user_id,
        "token_type": token_type,
        "exp": datetime.utcnow() + expires_delta,
        "session": str(uuid.uuid4()),
    }

    # Hardcode =(
    encoded_jwt = jwt.encode(to_encode, secret, algorithm="HS256")

    return encoded_jwt


def verify_jwt_token(
        token: str,
        context: Literal["email", "access", "refresh"],
        secret: str = "super_secret",  # NOT GOOD
) -> TokenData:
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(401, "Cant verify token")

    if payload["token_type"] != context:
        raise HTTPException(401, "Cant verify token type")

    return TokenData(**payload)
