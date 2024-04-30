from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os

load_dotenv()
DATABASE_URL = os.environ["MONGO_DB_URL"]

client = AsyncIOMotorClient(DATABASE_URL)
database = client.test