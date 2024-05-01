from langchain_openai import ChatOpenAI
from langchain_community.llms.moonshot import Moonshot

def _openai():
  return ChatOpenAI()

def _moonshot():
  return Moonshot(model="moonshot-v1-8k")

def get_llm():
  return _openai()