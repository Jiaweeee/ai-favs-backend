from pydantic import BaseModel
from typing import Optional

class AddCollectionBody(BaseModel):
    url: str

class DeleteCollectionBody(BaseModel):
    collection_id: str

class CollectionBase(BaseModel):
    url: str

class CollectionCreate(CollectionBase):
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None

    class Config:
        orm_mode = True