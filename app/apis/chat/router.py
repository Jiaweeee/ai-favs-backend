from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.apis.chat.chain import create_follow_ups_chain
from app.apis.schemas import BaseResponse
from .schemas import ChatRequest
from .agent import *

router = APIRouter()

@router.post("/chat", response_model=BaseResponse)
def chat(req: ChatRequest):
  agent = QuestionAnswerAgent()
  response = agent.run(req.input, req.chat_history)
  return BaseResponse(
    code=200,
    msg="success",
    data=response
  )

@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
  agent = QuestionAnswerAgent()
  return StreamingResponse(
    agent.stream(req.input, req.chat_history),
    media_type="text/event-stream"
  )


@router.get("/chat/followups/get", response_model=BaseResponse)
def chat_followups_get(req: ChatRequest):
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