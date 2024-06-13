from pydantic import BaseModel

class AddCollectionBody(BaseModel):
    url: str

class DeleteCollectionBody(BaseModel):
    collection_id: str