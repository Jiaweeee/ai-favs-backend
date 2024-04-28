from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Any
from .chain import create_chain
from langsmith import traceable

class CommonResponse(BaseModel):
  code: int
  msg: Optional[str] = None
  data: Optional[Any] = None

class ChatRequest(BaseModel):
  input: str
  chat_history: Optional[List[str]] = []

class ChatResponse(BaseModel):
  content: str
  sources: Optional[List[str]] = None
  suggested_questions: Optional[List[str]] = None

router = APIRouter()
rag_chain = create_chain()

@traceable
@router.post("/chat", response_model=CommonResponse)
async def chat(req: ChatRequest):
  response = rag_chain.invoke({
    "input": req.input,
    "chat_history": req.chat_history
  })
  answer = response["answer"]
  return CommonResponse(
    code=200,
    msg='success',
    data=ChatResponse(content=answer)
  )

__all__ = ["router"]