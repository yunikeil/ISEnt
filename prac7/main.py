from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="./static"), name="static")
events = ["message",]
" ".lower()

@app.post("/event_list")
async def new_event(value: dict):
    global events
    events = value["value"].strip().split(",")
    return "Updated!"

@app.get("/event_list_")
async def is_exists(event_: str):
    ev = []

    if event_.replace("  ", " ") == " ":
        raise HTTPException(404)

    if not event_:
        raise HTTPException(404)

    for event in events:
        if event_.lower() in event.lower():
            ev.append(event)

    if not ev:
        raise  HTTPException(404)

    return ev


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
