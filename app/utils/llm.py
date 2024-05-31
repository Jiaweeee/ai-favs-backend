from langchain_openai import ChatOpenAI
from langchain_community.llms.moonshot import Moonshot

def _openai(streaming: bool):
  return ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    streaming=streaming
  )

def _moonshot():
  return Moonshot(model="moonshot-v1-8k")

def get_llm(streaming: bool = False):
  return _openai(streaming)