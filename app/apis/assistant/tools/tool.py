from pydantic import BaseModel, Field
from langchain_core.utils.function_calling import convert_to_openai_tool
from typing import Type, Any, Literal
from abc import ABC, abstractmethod

ToolType = Literal[
    "ui",
    "data"
]

class Tool(ABC):
    name: str
    description: str
    type: ToolType
    input_schema: Type[BaseModel]
    
    @abstractmethod
    def call(self, **kwargs: Any) -> Any:
        pass

    def to_openai_tool(self):
        tool = convert_to_openai_tool(self.input_schema)
        function = tool["function"]
        function["name"] = self.name
        function["description"] = self.description
        return tool
    
class ReActToolInput(BaseModel):
    """Base schema of the tools that will be used in the ReAct prompting framework."""

    reasoning: str = Field(description=(
        "Reasoning is how the task will be accomplished with the current function. "
        "Detail your overall plan along with any concerns you have."
        "Ensure this reasoning value is in the user defined langauge "
    ))
    task_completed: bool = Field(description="Whether the original goal has been achieved.")
