from dotenv import load_dotenv
from pymongo import MongoClient

import os

load_dotenv()
DATABASE_URL = os.environ["MONGO_DB_URL"]

client = MongoClient(DATABASE_URL)
database = client.test