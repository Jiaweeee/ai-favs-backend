from pydantic import BaseModel, Field
from typing import Optional, List

class ContentAddRequest(BaseModel):
  url: str

class ContentItem(BaseModel):
  id: str = Field(...)
  url: str = Field(...)
  title: Optional[str] = None
  description: Optional[str] = None
  thumbnail: Optional[str] = None
  full_text: Optional[str] = None
  ai_labels: Optional[List[str]] = None
  ai_summary: Optional[str] = None
  ai_highlights: Optional[List[str]] = None
  ai_podcast_url: Optional[str] = None
