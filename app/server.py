from fastapi import FastAPI
from dotenv import load_dotenv
from .apis.chat.router import router as chat_router
from .apis.content.router import router as content_router
from .db import models, database
import logging

models.Base.metadata.create_all(bind=database.engine)
load_dotenv()
app = FastAPI()
logging.basicConfig(level=logging.INFO, format="%(asctime)s    %(levelname)s    %(message)s")

@app.get("/")
async def root():
    return "Welcome to AIFavs"

app.include_router(chat_router)
app.include_router(content_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
