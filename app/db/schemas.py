from pydantic import BaseModel
from typing import Optional, List

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str]

class Category(CategoryCreate):
    id: str
    name: str
    description: Optional[str]

class TagCreate(BaseModel):
    name: str

class Tag(TagCreate):
    id: str

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

class Collection(CollectionBase):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[Tag]] = None
    category: Optional[Category] = None