from pydantic import BaseModel
from app.apis.schemas import BaseResponse

class AddCollectionRequest(BaseModel):
    url: str
