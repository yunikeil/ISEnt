from fastapi import Depends

from app.depends import BaseUserSession, get_access
from core.database.session import context_get_pg_session


class UserService(BaseUserSession):

    async def __call__(self, token_data=Depends(get_access)):
        pass

    ...




