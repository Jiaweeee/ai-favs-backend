from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from .apis.chat.router import router as chat_router
from .apis.content.router import router as content_router
from .apis.podcast.router import router as podcast_router
from .db import models, database
import logging, os

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s    %(levelname)s    %(message)s")
logger = logging.getLogger(__file__)

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()

# create audio dir
audio_dir = "app/public/audio"
os.makedirs(audio_dir, exist_ok=True)
app.mount("/audio", StaticFiles(directory=audio_dir), name="audio")

# include routers
app.include_router(chat_router)
app.include_router(content_router)
app.include_router(podcast_router)

@app.get("/")
async def root():
    return "Welcome to AIFavs"

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
