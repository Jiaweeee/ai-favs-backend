from fastapi import APIRouter, BackgroundTasks, Query
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from typing import Optional
from app.apis.models import BaseResponse
from app.utils import vectorstore
from .models import ContentAddRequest, ContentItem
from .database import add_content, update_content, retrieve_content_items
from .chain import create_summary_chain, create_category_chain
import re, hashlib

router = APIRouter()

class WeChatArticleProcessor():
  def __init__(self, url: str):
    self.driver = self._get_chrome_driver()
    self.url = url
  
  def _get_chrome_driver(self) -> webdriver.Chrome:
    """
    Build and return a Chrome web driver
    """
    driver_path = 'libs/chromedriver'
    service = Service(executable_path=driver_path)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(service=service, options=options)

  def process(self):
    print("Start processing...")
    driver = self.driver
    driver.get(self.url)
    driver.implicitly_wait(5)
    # Extract content and metadata
    title = driver.find_element(By.XPATH, '//*[@property="og:title"]').get_attribute("content")
    description = driver.find_element(By.XPATH, '//*[@property="og:description"]').get_attribute("content")
    thumbnail = driver.find_element(By.XPATH, '//*[@property="og:image"]').get_attribute("content")
    print('Extract content and metadata: DONE')

    # Save the metadata into db
    content_item = add_content({
      "url": self.url,
      "title": title,
      "description": description,
      "thumbnail": thumbnail,
    })
    print('Save the metadata into db: DONE')

    # Save the content into vector store
    content = driver.find_element(by=By.CLASS_NAME, value="rich_media_content")
    if content:
      full_text = content.text
    if content_item and full_text:
      vectorstore.save_content(full_text, metadata={
        "content_id": content_item.id,
        "source": content_item.url
      })
      print('Save the content into vector store: DONE.')

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
        print(f"Generate useful info by LLM error: {e}")
      update_content(id=content_item.id, data=data)
      print("Generate useful info by LLM: DONE")

    # Set proper category for the content
    if content_item:
      self._update_category(item=content_item)
    
  def _update_category(self, item: ContentItem):
    items = retrieve_content_items()
    filtered_items = list(filter(lambda x: x.category != None, items))
    categories = list(map(lambda x : {"name": x.category.name, "description": x.category.description}, filtered_items))
    category_chain = create_category_chain()
    target_category = category_chain.invoke({"item": item, "categories": categories})
    print("Updating category")

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
  processor.process()
  print("parse url success")

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