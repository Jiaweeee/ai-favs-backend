from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from .chain import create_chain

class ChatRequest(BaseModel):
  input: str
  chat_history: Optional[List[str]] = None

class ChatResponse(BaseModel):
  answer: str
  sources: Optional[List[str]] = None

router = APIRouter()
rag_chain = create_chain()

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
  response = rag_chain.invoke({
    "input": req.input,
    "chat_history": []
  })
  answer = response["answer"]
  return ChatResponse(
    answer=answer,
    sources=["www.baidu.com", "www.google.com"]
  )

__all__ = ["router"]