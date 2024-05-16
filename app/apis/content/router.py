from fastapi import APIRouter, BackgroundTasks, Query
from typing import Optional
from app.apis.models import BaseResponse
from .models import ContentAddRequest
from .database import (
  insert_content_item,
  update_content_item,
  retrieve_content_item,
  retrieve_all_content_items,
  retrieve_content_items_by_category,
  retrieve_categories
)
from app.utils import vectorstore
from .chain import create_summary_chain, create_category_chain
from .processors import WeChatArticleProcessor
import re, hashlib, logging

router = APIRouter()
logger = logging.getLogger(__name__)

def is_wechat_article(url) -> bool:
  """
  Check if the url is from wechat official account article.
  """
  pattern = r'^https?://mp\.weixin\.qq\.com/s'
  if re.match(pattern, url):
    return True
  return False

def generate_summary_by_ai(url: str):
  logger.info(f"Generating summary by ai. url = {url}")
  item = retrieve_content_item(url=url)
  if item:
    chain = create_summary_chain()
    response = chain.invoke({"content": item.full_text})
    data = {}
    try:
      data["ai_labels"] = response["labels"]
      data["ai_summary"] = response["summary"]
      data["ai_highlights"] = response["highlights"]
      update_content_item(id=item.id, data=data)
      logger.info("Generating summary by ai: DONE")
    except Exception as e:
      logger.error(f"Generate summary by ai error: {e}")

def generate_category_by_ai(url: str):
  logger.info(f"Generating category by ai. url = {url}")
  item = retrieve_content_item(url=url)
  if item:
    categories = retrieve_categories()
    category_chain = create_category_chain()
    target_category = category_chain.invoke({"item": item, "categories": categories})
    logger.info(f"Updating category, category = {target_category}")

    def generate_category_id(name: str):
      return hashlib.sha1(name.encode()).hexdigest()

    update_content_item(item.id, {
      "category": {
        "id": generate_category_id(target_category["name"]),
        "name": target_category["name"],
        "description": target_category["description"]
      }
    })

def save_to_vector_store(url: str):
  logger.info(f"Saving content to vector store. url = {url}")
  item = retrieve_content_item(url=url)
  if item and item.full_text:
    vectorstore.save_content(item.full_text, metadata={
      "content_id": item.id,
      "source": url
    })
    logger.info(f"Save content to vector store, Done. url = {url}")

@router.post("/content/add", response_model=BaseResponse)
async def content_add(req: ContentAddRequest, background_tasks: BackgroundTasks):
  if not is_wechat_article(req.url):
    return BaseResponse(
      code=500,
      msg='Content not support.'
    )
  url = req.url
  processor = WeChatArticleProcessor()
  item = retrieve_content_item(url=url)
  if item:
    return BaseResponse(
      code=200,
      msg='Content already exist'
    )
  else:
    data = await processor.run_async(url)
    insert_content_item(data)
    background_tasks.add_task(generate_summary_by_ai, url)
    background_tasks.add_task(generate_category_by_ai, url)
    background_tasks.add_task(save_to_vector_store, url)
    return BaseResponse(
      code=200,
      msg='success'
    )

@router.get("/content/list/get", response_model=BaseResponse)
async def get_content_list(category_id: Optional[str]=Query(None)):
  if category_id:
    items = retrieve_content_items_by_category(category_id)
  else:
    items = retrieve_all_content_items()
  return BaseResponse(
    code=200,
    msg='success',
    data=items
  )

__all__ = ["router"]