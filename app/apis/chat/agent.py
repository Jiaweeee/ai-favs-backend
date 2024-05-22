from app.utils.llm import get_llm
from app.utils.vectorstore import load_vector_store
from langchain.agents import create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools.retriever import create_retriever_tool
from pydantic import BaseModel
import json

class Event(BaseModel):
    name: str
    msg: str

class QuestionAnswerAgent:
    def __init__(self) -> None:
        self.prompt = """
        - Role: Knowledge Base Assistant

        - Background: AiFavs is a read-it-later app similar to Pocket. \
        It allows user save contents on the internet to a local knowledge base \
        and interact with it later. It has a built-in AI assistant which aims to \
        help the user better understand the saved content.

        - Profile: You are an AI Agent designed to efficiently retrieve and synthesize \
        information from a local vector database and the internet to answer user queries.

        - Skills: Vector database querying, internet search, information synthesis, \
        natural language understanding.

        - Goals: To provide accurate and relevant answers to user queries by first \
        searching the local knowledge base and then, if needed, using the internet search tool.

        - Constraints: Ensure the response is accurate, relevant, and synthesized \
        from the most reliable sources available.
        - OutputFormat: Textual response that directly addresses the user's query.
        """
        self.tools = [
            self._web_search(),
            self._vector_store_search()
        ]

    def _web_search(self):
        return TavilySearchResults(max_results=5)
    
    def _vector_store_search(self):
        vector_store = load_vector_store()
        return create_retriever_tool(
            vector_store.as_retriever(),
            name="knowledge_base_search",
            description="Search for relevant content in the local vector database"
        )

    def _get_executor(self) -> AgentExecutor:
        llm = get_llm()
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
            response: Event
            if kind == "on_chain_start":
                if event["name"] == "Agent":
                    response = Event(
                        name="start",
                        msg=f"Starting agent: {event['name']} with input: {event['data'].get('input')}"
                    )
            elif kind == "on_chain_end":
                if event["name"] == "Agent":
                    response = Event(
                        name="end",
                        msg=f"Done agent: {event['name']} with output: {event['data'].get('output')['output']}"
                    )
            elif kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    response = Event(
                        name="answering",
                        msg=content
                    )
            elif kind == "on_tool_start":
                response = Event(
                    name="use_tool_start",
                    msg=f"Starting tool: {event['name']} with inputs: {event['data'].get('input')}"
                )
            elif kind == "on_tool_end":
                response = Event(
                    name="use_tool_end",
                    msg=f"Done tool: {event['name']}\nTool output was: {event['data'].get('output')}"
                )
            yield json.dumps(response, default=custom_serializer) + "\n"

