from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from langsmith import traceable
from app.apis.chat.chain import create_chain
from app.apis.models import CommonResponse

class ChatRequest(BaseModel):
  input: str
  chat_history: Optional[List[str]] = []

class ChatResponse(BaseModel):
  content: str
  sources: Optional[List[str]] = None
  suggested_questions: Optional[List[str]] = None

router = APIRouter()

@traceable
@router.post("/chat", response_model=CommonResponse)
async def chat(req: ChatRequest):
  rag_chain = create_chain()
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