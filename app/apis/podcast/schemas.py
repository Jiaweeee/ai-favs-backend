from pydantic import BaseModel
from typing import Optional

class PodcastCreateRequestBody(BaseModel):
    collection_id: str

class PodcastBase(BaseModel):
    id: str
    title: str
    status: int
    file_path: Optional[str] = None
    transcript: Optional[str] = None

class PodcastCreate(PodcastBase):

    class Config:
        orm_mode = True

class PodcastResponse(PodcastBase):
    collection_id: str
    collection_url: str