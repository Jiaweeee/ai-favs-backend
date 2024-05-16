from playwright.async_api import async_playwright
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseProcessor(ABC):
  @abstractmethod
  async def run_async(self, url) -> dict:
    pass

class WeChatArticleProcessor(BaseProcessor):
  async def run_async(self, url) -> dict:
    async with async_playwright() as playwright:
      logger.info("Start processing...")
      browser = await playwright.chromium.launch(headless=True)
      page = await browser.new_page()
      await page.goto(url)
      
      title_element = await page.query_selector('meta[property="og:title"]')
      title = await title_element.get_attribute("content")
      
      description_element = await page.query_selector('meta[property="og:description"]')
      description = await description_element.get_attribute("content")
      
      thumbnail_element = await page.query_selector('meta[property="og:image"]')
      thumbnail = await thumbnail_element.get_attribute("content")
      
      full_text_element = await page.query_selector(".rich_media_content")
      full_text = await full_text_element.text_content()

      await browser.close()
      logger.info('Extract content and metadata: DONE')
      return {
        "url": url,
        "title": title,
        "description": description,
        "thumbnail": thumbnail,
        "full_text": full_text
      }