from typing import Any, Literal, Annotated
from abc import ABC, abstractmethod

from fastapi.security import APIKeyCookie
from fastapi import Depends, HTTPException, status, WebSocketException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import provide_pg_session, context_get_pg_session
from core.security.tokens import verify_jwt_token


access_token_scheme = APIKeyCookie(
    name="access",
    scheme_name="Cookie access token",
    description="Не трогай если не знаешь зачем это.",
    auto_error=False,
)
refresh_token_scheme = APIKeyCookie(
    name="refresh",
    scheme_name="Cookie refresh token",
    description="Не трогай если не знаешь зачем это.",
    auto_error=False,
)


async def get_access(access_t: str = Depends(access_token_scheme)):
    return verify_jwt_token(access_t, "access")


async def get_refresh(refresh_t=Depends(refresh_token_scheme)):
    return verify_jwt_token(refresh_t, "refresh")


class BaseUserSession(ABC):
    request_method: Literal[
        "http",
        "ws"
    ]

    def __init__(self, query_options = None, query_args = None):
        """
        :param query_options: Опции для отложенной загрузки sqlalchemy
        :param query_args:  Параметры настройки отложенной загрузки
        """
        self.__options = None
        if query_options and query_args:
            self.__options = (query_options, query_args)

    @abstractmethod
    async def __call__(self, token_data = Depends(get_access)):
        pass

    def _raise(self, code, comment):
        match self.request_method:
            case "http":
                raise HTTPException(
                    status_code=code,
                    detail=comment,
                )
            case "ws":
                raise WebSocketException(
                    code=status.WS_1000_NORMAL_CLOSURE,
                    reason=comment,
                )
            case _:
                raise  HTTPException(500, "Unknown request method, please contact @dev_backend_duty group")


AsyncSessionDep = Annotated[AsyncSession, Depends(context_get_pg_session())]
