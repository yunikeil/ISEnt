from typing import Literal, cast
import random

from fastapi.exceptions import HTTPException
from starlette import status

from core.redis.client import get_redis_client

CodesContextT = Literal["new_user_verify", "old_user_login"]


class Codes:
    @staticmethod
    def _generate_secret_number(length: int = 4) -> int:
        min_value = 10 ** (length - 1)
        max_value = (10 ** length) - 1
        return random.randint(min_value, max_value)

    @classmethod
    async def verify(
        cls, user_id: int, code: int, context: CodesContextT,
    ):
        right_code, data = await cls.get(user_id=user_id, context=context)
        if code == right_code:
            await cls.delete(user_id, context)
            return True, cast(bytes, data).decode() if data else None

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    @classmethod
    async def generate(
        cls, user_id: int, context: CodesContextT, data: str = "NaN", ttl: int = 900,
    ):
        async with get_redis_client() as redis:
            code = cls._generate_secret_number()
            await redis.setex(f"{user_id}:{context}", ttl, f"{code}:{data}")

        return code

    @staticmethod
    async def delete(user_id: int, context: CodesContextT):
        async with get_redis_client() as redis:
            await redis.delete(f"{user_id}:{context}")

    @staticmethod
    async def get(user_id: int, context: CodesContextT):
        async with get_redis_client() as redis:
            result: str = await redis.get(f"{user_id}:{context}")
            if result:
                code, data = result.split(b":")
                return int(code), data if data != b"NaN" else None

            return None, None