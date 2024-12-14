from fastapi import FastAPI, Form, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
fake_db = {
    "user1": {"password": "password123", "token": "dummy_token_123"},
}

class LoginForm(BaseModel):
    username: str
    password: str

@app.get("/protected")
async def protected_page(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login"))):
    if token == "dummy_token_123":
        return {"message": "Welcome to the protected page!"}
    else:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})

@app.post("/login")
async def login(form_data: LoginForm):
    user = fake_db.get(form_data.username)
    if user and user["password"] == form_data.password:
        return {"access_token": user["token"], "token_type": "bearer"}
    return JSONResponse(status_code=401, content={"message": "Invalid credentials"})

@app.get("/")
async def read_root():
    return {"message": "Welcome to the login page"}
