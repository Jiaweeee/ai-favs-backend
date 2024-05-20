from pydantic import BaseModel, Field
from typing import Optional, List
from langchain_core.messages import HumanMessage, AIMessage

Message = HumanMessage | AIMessage

class ChatRequest(BaseModel):
  input: str
  chat_history: Optional[List[Message]] = []

class ChatResponse(BaseModel):
  content: str
  sources: Optional[List[str]] = None