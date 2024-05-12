from pymongo.errors import DuplicateKeyError
from app.apis.database import database as db
from bson.objectid import ObjectId
from .models import ContentItem, ContentCategory
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

def retrieve_content_items(category_id: Optional[str] = None):
  items = []
  if category_id:
    cursor = content_collection.find({"category.id": category_id})
  else:
    cursor = content_collection.find()
  for item in cursor.sort({"_id": -1}): # sort by time, descending
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
    ai_podcast_url=data.get('ai_podcast_url', None),
    category=to_category(data.get("category", None))
  )

def to_category(data: dict) -> ContentCategory:
  if data == None:
    return None
  return ContentCategory(
    id=data["id"],
    name=data["name"],
    description=data["description"]
  )