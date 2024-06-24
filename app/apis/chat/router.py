from fastapi import APIRouter, status as HttpStatus, Depends
from fastapi.responses import StreamingResponse
from app.apis.chat.chain import create_follow_ups_chain
from app.apis.schemas import BaseResponse
from app.apis.dependencies import get_current_user
from app.db import models
from .schemas import ChatRequest
from .agent import *

router = APIRouter()

@router.post("/chat", response_model=BaseResponse)
def chat(req: ChatRequest, current_user: models.User = Depends(get_current_user)):
  agent = QuestionAnswerAgent(user_id=current_user.id)
  response = agent.run(req.input, req.chat_history)
  return BaseResponse(
    code=HttpStatus.HTTP_200_OK,
    msg="success",
    data=response
  )

@router.post("/chat/stream")
def chat_stream(req: ChatRequest, current_user: models.User = Depends(get_current_user)):
  agent = QuestionAnswerAgent(user_id=current_user.id)
  return StreamingResponse(
    agent.stream(req.input, req.chat_history),
    media_type="text/event-stream"
  )


@router.get("/chat/followups/get", response_model=BaseResponse)
def chat_followups_get(req: ChatRequest, current_user: models.User = Depends(get_current_user)):
  follow_ups_chain = create_follow_ups_chain()
  response = follow_ups_chain.invoke({
    "input": req.input,
    "chat_history": req.chat_history
  })
  return BaseResponse(
    code=HttpStatus.HTTP_200_OK,
    msg='success',
    data=response
  )

__all__ = ["router"]