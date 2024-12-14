## Практическая работа 7

## Файл для синхронизации

```python
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

```


## Отправка данных

```js
function sendRequest() {
    const inputField = document.getElementById('inputField');
    const data = {
        "value": inputField.value
    };

    fetch('http://localhost:8000/event_list', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function onInputChange() {
    clearTimeout(timeout);
    timeout = setTimeout(sendRequest, 500);
}
```

Отрисовка данных:

```js
async function fetchEvents() {
    const event = document.getElementById('event').value;
    const url = `http://localhost:8000/event_list_?event_=${encodeURIComponent(event)}`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        const resultContainer = document.getElementById('results');
        resultContainer.innerHTML = '';

        if (data.length > 0) {
            data.forEach(event => {
                const eventElement = document.createElement('li');
                eventElement.textContent = event;
                resultContainer.appendChild(eventElement);
            });
        } else {
            resultContainer.innerHTML = '<li>События не найдены</li>';
        }
    } catch (error) {
        console.error('Ошибка при получении данных:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const eventInput = document.getElementById('event');
    eventInput.addEventListener('input', fetchEvents);
});

```