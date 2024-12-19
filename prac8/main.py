import asyncio
import urllib
import requests
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

app = FastAPI()

@app.post("/anime_search/")
async def anime_search(url: str):
    # if file:
    #     url = f"data:image/jpeg;base64,{(await file.read()).hex()}"

    encoded_url = urllib.parse.quote_plus(url)

    response = requests.get(f"https://api.trace.moe/search?url={encoded_url}")
    response.raise_for_status()
    data = response.json()

    results = data.get("result", [])
    if not results:
        return JSONResponse(content={"message": "Результаты не найдены."}, status_code=404)


    return JSONResponse(content={
        "frame_count": data.get("frameCount"),
        "results": results
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
