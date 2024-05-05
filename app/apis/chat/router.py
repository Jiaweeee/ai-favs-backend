from fastapi import APIRouter
from langsmith import traceable
from app.apis.chat.chain import create_rag_chain, create_follow_ups_chain
from app.apis.models import BaseResponse
from .models import ChatRequest, ChatResponse

router = APIRouter()

@traceable
@router.post("/chat", response_model=BaseResponse)
async def chat(req: ChatRequest):
  rag_chain = create_rag_chain()
  response = rag_chain.invoke({
    "input": req.input,
    "chat_history": req.chat_history
  })
  answer = response["answer"]
  return BaseResponse(
    code=200,
    msg='success',
    data=ChatResponse(content=answer)
  )

@router.get("/chat/followups/get", response_model=BaseResponse)
async def chat_followups_get(req: ChatRequest):
  follow_ups_chain = create_follow_ups_chain()
  response = follow_ups_chain.invoke({
    "input": req.input,
    "chat_history": req.chat_history
  })
  return BaseResponse(
    code=200,
    msg='success',
    data=response
  )

__all__ = ["router"]