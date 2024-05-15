from fastapi import APIRouter, BackgroundTasks, Query
from playwright.sync_api import sync_playwright, Browser
from typing import Optional
from app.apis.models import BaseResponse
from app.utils import vectorstore
from .models import ContentAddRequest, ContentItem
from .database import add_content, update_content, retrieve_content_items, retrieve_categories
from .chain import create_summary_chain, create_category_chain
import re, hashlib, logging

router = APIRouter()
logger = logging.getLogger(__name__)

class WeChatArticleProcessor():
  def __init__(self, url: str):
    self.url = url
  
  def _get_browser(self) -> Browser:
    with sync_playwright() as playwright:
      chromium = playwright.chromium
      browser = chromium.launch(headless=True)
      return browser

  def run(self):
    logger.info("Start processing...")
    with sync_playwright() as playwright:
      chromium = playwright.chromium
      browser = chromium.launch(headless=True)
      page = browser.new_page()
      page.goto(self.url)
      title = page.query_selector('meta[property="og:title"]').get_attribute("content")
      description = page.query_selector('meta[property="og:description"]').get_attribute("content")
      thumbnail = page.query_selector('meta[property="og:image"]').get_attribute("content")
      logger.info('Extract content and metadata: DONE')

      # Save the metadata into db
      content_item = add_content({
        "url": self.url,
        "title": title,
        "description": description,
        "thumbnail": thumbnail,
      })
      logger.info('Save the metadata into db: DONE')

      # Save the content into vector store
      content_element = page.query_selector(".rich_media_content")
      if content_element:
        full_text = content_element.text_content()
      browser.close()
      if content_item and full_text:
        vectorstore.save_content(full_text, metadata={
          "content_id": content_item.id,
          "source": content_item.url
        })
        logger.info('Save the content into vector store: DONE.')

      # Generate useful info by LLM
      if content_item and full_text:
        chain = create_summary_chain()
        response = chain.invoke({"content": full_text})
        data = {}
        try:
          data["ai_labels"] = response["labels"]
          data["ai_summary"] = response["summary"]
          data["ai_highlights"] = response["highlights"]
        except Exception as e:
          logger.error(f"Generate useful info by LLM error: {e}")
        update_content(id=content_item.id, data=data)
        logger.info("Generate useful info by LLM: DONE")

      # Set proper category for the content
      if content_item:
        self._update_category(item=content_item)
    
  def _update_category(self, item: ContentItem):
    categories = retrieve_categories()
    category_chain = create_category_chain()
    target_category = category_chain.invoke({"item": item, "categories": categories})
    logger.info("Updating category")

    def generate_category_id(name: str):
      return hashlib.sha1(name.encode()).hexdigest()

    update_content(item.id, {
      "category": {
        "id": generate_category_id(target_category["name"]),
        "name": target_category["name"],
        "description": target_category["description"]
      }
    })

def is_wechat_article(url) -> bool:
  """
  Check if the url is from wechat official account article.
  """
  pattern = r"https://mp\.weixin\.qq\.com/s/[a-zA-Z0-9_-]+"
  if re.match(pattern, url):
    return True
  return False


def process_content(url: str):
  if is_wechat_article(url) == False:
    # Only support wechat article for now.
    raise Exception("unsupported content source")

  processor = WeChatArticleProcessor(url=url)
  processor.run()
  logger.info("parse url success")

@router.post("/content/add", response_model=BaseResponse)
async def content_add(req: ContentAddRequest, background_tasks: BackgroundTasks):
  background_tasks.add_task(process_content, req.url)
  return BaseResponse(
    code=200,
    msg='success'
  )

@router.get("/content/list/get", response_model=BaseResponse)
async def get_content_list(category_id: Optional[str]=Query(None)):
  items = retrieve_content_items(category_id)
  return BaseResponse(
    code=200,
    msg='success',
    data=items
  )

__all__ = ["router"]