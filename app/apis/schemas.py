from typing import Optional, Any
from pydantic import BaseModel

class BaseResponse(BaseModel):
    """
    The standard response data structure for all apis.
    """
    code: int
    msg: Optional[str] = None
    data: Optional[Any] = None
