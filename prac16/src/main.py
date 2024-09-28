import os
import json
import logging
import secrets
from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from core.database.session import test_pg_connection
from core.redis.client import get_redis_client
from core.settings import config

from app.routers import user_router, auth_router


security = HTTPBasic()
origins = [
    "http://localhost:80",
    "http://localhost:3000",
    "https://auth.yunikeil.ru",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    uvi_access_logger = logging.getLogger("uvicorn.access")
    uvi_base_logger = logging.getLogger("uvicorn")

    async with get_redis_client() as client:
        await client.ping()

    await test_pg_connection()

    yield


app = FastAPI(
    openapi_url=None,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(auth_router)


def __temp_get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"yunikeil"
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"yunikeil"
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/", include_in_schema=False)
async def redirect_root():
    return RedirectResponse(url="/docs")


@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation(_: str = Depends(__temp_get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(__temp_get_current_username)):
    return get_openapi(title=f"AuthPrac Title, logged: {username}", version="1.0.0", routes=app.routes)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="main:app",
        host="app-authprac",
        port=8080,
        reload=config.RELOAD,
    )