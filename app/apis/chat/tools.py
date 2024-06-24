from abc import ABC, abstractmethod
from langchain_core.tools import BaseTool
from langchain_community.tools.tavily_search import TavilySearchResults
from app.utils.vectorstore import load_vector_store_by_index
from langchain.tools.retriever import create_retriever_tool

class Tool(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def get(self) -> BaseTool:
        pass

class WebSearch(Tool):

    def get(self) -> BaseTool:
        return TavilySearchResults(max_results=5)

class VectorStoreSearch(Tool):
    def __init__(self, index_name) -> None:
        self.index_name = index_name

    def get(self) -> BaseTool:
        vector_store = load_vector_store_by_index(
            index_name=self.index_name
        )
        return create_retriever_tool(
            vector_store.as_retriever(),
            name="knowledge_base_search",
            description="Search for relevant content in the local vector database"
        )