import app.utils.llm as LLM
from langchain.agents import create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor
from pydantic import BaseModel
from typing import Literal, Dict
from .tools import *
import json

EventType = Literal[
    "start",
    "tool_start",
    "tool_end",
    "llm_streaming",
    "end"
]

event_map: Dict[str, EventType] = {
    "on_chain_start": "start",
    "on_tool_start": "tool_start",
    "on_chat_model_stream": "llm_streaming",
    "on_tool_end": "tool_end",
    "on_chain_end": "end"
}

class AgentStreamEvent(BaseModel):
    event: EventType

class ToolUseEvent(AgentStreamEvent):
    tool_name: str
    tool_description: str

class LLMStreamingEvent(AgentStreamEvent):
    event: EventType = "llm_streaming"
    content: str

class StreamEndEvent(AgentStreamEvent):
    event: EventType = "end"
    output: str
    
class QuestionAnswerAgent:
    def __init__(self, user_id: str) -> None:
        self.prompt = """
        You are a helpful assistant. There's a local knowledge base that you can access. \
        If you not sure about the answer of a user query, you should ALWAYS search the local \
        knowledge base for context. If nothing relavent found, then search on the internet.
        """
        self.tools = [
            WebSearch().get(),
            VectorStoreSearch(index_name=user_id).get()
        ]

    def _get_executor(self) -> AgentExecutor:
        llm = LLM.get_tool_calling_model(streaming=True)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.prompt),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        tools = self.tools
        agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
        return AgentExecutor(
            agent=agent,
            tools=tools,
            max_execution_time=60,
            verbose=True
        ).with_config({"run_name": "Agent"})

    def run(self, query: str, chat_history: list = []):
        agent_executor = self._get_executor()
        return agent_executor.invoke({"input": query, "chat_history": chat_history})
    
    async def stream(self, query, chat_history: list = []):
        agent_executor = self._get_executor()
        def custom_serializer(obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            else:
                return str(obj)
        
        async for event in agent_executor.astream_events(
            {"input": query, "chat_history": chat_history},
            version="v1"
        ):
            kind = event["event"]
            result: AgentStreamEvent
            if kind == "on_chain_start":
                if event["name"] == "Agent":
                    result = AgentStreamEvent(event="start")
            elif kind == "on_chain_end":
                if event["name"] == "Agent":
                    result = StreamEndEvent(output=event["data"]["output"]["output"])
            elif kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    result = LLMStreamingEvent(content=content)
            elif kind == "on_tool_start":
                result = ToolUseEvent(
                    event="tool_start",
                    tool_name=event["name"],
                    tool_description=""
                )
            elif kind == "on_tool_end":
                result = ToolUseEvent(
                    event="tool_end",
                    tool_name=event["name"],
                    tool_description=""
                )
            data = json.dumps(result, default=custom_serializer)
            yield f"data: {data}\n\n"

