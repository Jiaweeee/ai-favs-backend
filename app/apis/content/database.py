from pymongo.errors import DuplicateKeyError
from app.apis.database import database as db
from bson.objectid import ObjectId
from .models import ContentItem
from typing import Optional

content_collection = db.get_collection("content_items")
content_collection.create_index("url", unique=True)

async def add_content(data: dict) -> Optional[ContentItem]:
  print('add_content')
  try:
    item = await content_collection.insert_one(data)
    new_item = await content_collection.find_one({"_id": item.inserted_id})
    return to_content_item(new_item)
  except DuplicateKeyError:
    print("A content item with the same URL already exists.")
    return None
  

async def update_content(id: str, data: dict) -> bool:
  item = await content_collection.find_one({"_id", ObjectId(id)})
  if item:
    updated_item = await content_collection.update_one({
      {"_id": ObjectId(id)},
      {"$set", data}
    })
    if updated_item:
      return True
    return False

def to_content_item(data: dict) -> ContentItem:
  return ContentItem(
    id=str(data["_id"]),
    url=data["url"],
    title=data["title"],
    description=data["description"],
    thumbnail=data["thumbnail"]
  )