from pymongo.errors import DuplicateKeyError
from app.apis.database import database as db
from bson.objectid import ObjectId
from .models import ContentItem
from typing import Optional

content_collection = db.get_collection("content_items")
content_collection.create_index("url", unique=True)

def add_content(data: dict) -> Optional[ContentItem]:
  print('add_content')
  try:
    item = content_collection.insert_one(data)
    new_item = content_collection.find_one({"_id": item.inserted_id})
    return to_content_item(new_item)
  except DuplicateKeyError:
    print("A content item with the same URL already exists.")
    return None  

def update_content(id: str, data: dict) -> bool:
  item = content_collection.find_one({"_id": ObjectId(id)})
  if item:
    updated_item = content_collection.update_one(
      {"_id": ObjectId(id)},
      {"$set": data}
    )
    return updated_item.matched_count > 0
  return False

def retrieve_content_items():
  items = []
  for item in content_collection.find():
    items.append(to_content_item(item))
  return items

def to_content_item(data: dict) -> ContentItem:
  return ContentItem(
    id=str(data["_id"]),
    url=data["url"],
    title=data["title"],
    description=data["description"],
    thumbnail=data["thumbnail"],
    ai_labels=data.get('ai_labels', None),
    ai_highlights=data.get('ai_highlights', None),
    ai_summary=data.get('ai_summary', None),
    ai_podcast_url=data.get('ai_podcast_url', None)
  )