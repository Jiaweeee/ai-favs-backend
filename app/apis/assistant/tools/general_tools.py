from typing import Any
from pydantic import Field
from .tool import Tool, ReActToolInput

class ShowSummaryInput(ReActToolInput):
    msg: str = Field(description="The message to inform the user the task result.")

class ShowSummary(Tool):
    name = "show_summary"
    description = (
        "Useful when you think the goal is achieved and should show a summarized result to the user."
        "Rememeber: you should only use this tool to summarize the information you get from other tools."
        "You should NOT use this tool directly to answer the user query."
    )
    type = "ui"
    input_schema = ShowSummaryInput

    def call(self, msg: str) -> Any:
        return {
            "msg": msg
        }
    