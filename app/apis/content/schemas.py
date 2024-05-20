from pydantic import BaseModel

class ContentAddRequest(BaseModel):
  url: str