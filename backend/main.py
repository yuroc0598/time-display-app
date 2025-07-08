from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")


@app.get("/api/time")
async def get_current_time():
    return {"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


@app.get("/")
async def read_root():
    return FileResponse("../frontend/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, access_log=False)
