from typing import Any, Optional
from pydantic import Field
from .tool import Tool, ReActToolInput
from app.db.models import Collection
from sqlalchemy.orm import Session, defer

class GetCollectionInput(ReActToolInput):
    collection_id: str = Field(description="The unique id for the collection stored in the database.")

class GetCollection(Tool):
    name = "get_collection"
    description = "Useful when you want to get the information of a single article."
    type = "ui"
    input_schema = GetCollectionInput

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def call(self, collection_id: str) -> Any:
        collection = Collection.get(session=self.db_session, id_=collection_id)
        return {
            "title": collection.title,
            "id": collection.id,
            "description": collection.description,
            "summary": collection.summary,
            "created_at": collection.created_at
        }
    
class GetCollectionListInput(ReActToolInput):
    user_id: str = Field(description="")

class GetCollectionList(Tool):
    name = "get_collection_list"
    description = "Retrieve all the articles the user have saved."
    type = "ui"
    input_schema = GetCollectionListInput

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
    
    def call(self, user_id: str) -> Any:
        exclude_fields = ["category_id", "content", "user_id"]
        options = [defer(getattr(Collection, field)) for field in exclude_fields]
        collections = self.db_session.query(Collection)\
            .filter(Collection.user_id == user_id)\
            .options(*options)\
            .all()
        return [{
            "title": collection.title,
            "id": collection.id,
            "description": collection.description,
            "summary": collection.summary,
            "created_at": collection.created_at
        } for collection in collections]
                    