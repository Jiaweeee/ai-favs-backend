from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from .apis.chat.router import router as chat_router
from .apis.collection.router import router as collection_router
from .apis.podcast.router import router as podcast_router
from .apis.user.router import router as user_router
from .apis.assistant.router import router as assistant_router
from .db import models, database
import logging, os

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s    %(levelname)s    %(message)s")
logger = logging.getLogger(__file__)

app = FastAPI()

# create audio dir
audio_dir = "app/public/audio"
os.makedirs(audio_dir, exist_ok=True)
app.mount("/audio", StaticFiles(directory=audio_dir), name="audio")

# init database
db_dir = "app/db/files"
os.makedirs(db_dir, exist_ok=True)
models.Base.metadata.create_all(bind=database.engine)

# init vector store
vector_store_dir = "app/vectorestore"
os.makedirs(vector_store_dir, exist_ok=True)

# include routers
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(collection_router)
app.include_router(podcast_router)
app.include_router(assistant_router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal Server Error",
            "data": None
        }
    )

@app.get("/")
async def root():
    return "Welcome to AIFavs"

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
