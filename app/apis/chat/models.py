from pydantic import BaseModel, Field
from typing import Optional, List
from langchain_core.messages import BaseMessage

class ChatRequest(BaseModel):
  input: str
  chat_history: Optional[List[BaseMessage]] = []

class ChatResponse(BaseModel):
  content: str
  sources: Optional[List[str]] = None

class ChatFollowUps(BaseModel):
  follow_ups: List[str] = Field(default=[], description="A list of no more than 5 potential follow-up questions that could continue the conversation.")