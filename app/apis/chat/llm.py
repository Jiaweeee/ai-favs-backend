from langchain_openai import ChatOpenAI
from langchain_community.llms.moonshot import Moonshot

def openai():
  return ChatOpenAI()

def moonshot():
  return Moonshot(model="moonshot-v1-8k")