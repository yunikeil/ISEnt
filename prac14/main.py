from fastapi import FastAPI

app = FastAPI()

counter = 0

@app.get("/")
async def get_counter():
    global counter
    counter += 1
    print(counter)
    return {"count": counter}

# ab -n 10000 -c 50 http://localhost:8000/

# without cache nginx/direct (1 worker)
# rps 978.23/1020.54
# with cache nginx/direct (cache only on nginx) (1 worker)
# rps 2584.46/1035.09
