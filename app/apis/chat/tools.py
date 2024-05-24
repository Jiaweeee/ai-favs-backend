from abc import ABC, abstractmethod
from langchain_core.tools import BaseTool
from langchain_community.tools.tavily_search import TavilySearchResults
from app.utils.vectorstore import load_vector_store
from langchain.tools.retriever import create_retriever_tool

class Tool(ABC):
    name: str = ""
    msg_on_working: str = ""

    def __init__(self) -> None:
        pass

    @abstractmethod
    def get(self) -> BaseTool:
        pass

class WebSearch(Tool):
    name = "Web search"
    msg_on_working = "Searching the web..."

    def get(self) -> BaseTool:
        return TavilySearchResults(max_results=5)

class VectorStoreSearch(Tool):
    name = "Vector store search"
    msg_on_working = "Searching local knowledge base..."

    def get(self) -> BaseTool:
        vector_store = load_vector_store()
        return create_retriever_tool(
            vector_store.as_retriever(),
            name="knowledge_base_search",
            description="Search for relevant content in the local vector database"
        )