from abc import ABC, abstractmethod
from .tools.tool import Tool
from .tools.collection_tools import GetCollection, GetCollectionList
from .tools.general_tools import ShowSummary
from typing import List, Optional
from sqlalchemy.orm import Session

class Agent(ABC):
    name: str
    role_description: str

    @abstractmethod
    def get_tools(self) -> List[Tool]:
        pass
    
    def get_tool_from_name(self, name: str) -> Optional[Tool]:
        for tool in self.get_tools():
            if tool.name == name:
                return tool
        return None
    
class CollectionAgent(Agent):
    name = "collection_agent"
    role_description = (
        "You are a helpful AI assistant."
        "You can help users to achieve the goal they requested with the help of using correct tools."
    )

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def get_tools(self) -> List[Tool]:
        return [
            GetCollection(db_session=self.db_session),
            GetCollectionList(db_session=self.db_session),
            ShowSummary()
        ]

class RouterAgent(Agent):
    """
    Resolve the user query, construct an executable task and dispatch
    it to the correct agent to execute.
    """
    name = "router_agent"
    role_description = "" #TODO: routes the query to other agents

    def get_tools(self) -> List[Tool]:
        return [] #TODO