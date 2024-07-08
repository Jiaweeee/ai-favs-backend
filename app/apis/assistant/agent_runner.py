from pydantic import BaseModel
from .agent import Agent
from .tools.tool import Tool
from typing import Literal, Optional, Any, List
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, SystemMessagePromptTemplate
from app.utils.llm import get_tool_calling_model
from app.db.models import User

AgentActionType = Literal[
    "run",
    "error",
    "interrupt",
    "finish"
]

class ToolCall(BaseModel):
    name: str
    args: str
    result: Optional[Any] = None

class AgentAction(BaseModel):
    type: AgentActionType = "run"
    reasoning: Optional[str] = None
    tool_call: Optional[ToolCall] = None

    def format_action(self):
        reasoning = self.reasoning
        if self.tool_call:
            tool_name = self.tool_call.name
            tool_args = self.tool_call.args
            tool_result = self.tool_call.result
        return f"""
        Thought: {reasoning}
        Action: tool_name = `{tool_name}`, tool_args = `{tool_args}`
        Observation: {tool_result}

        """

class AgentRunner:
    def __init__(
        self,
        goal: str,
        agent: Agent,
        user: User,
        max_iteration: int = 10,
        completed_actions: List[AgentAction] = []
    ) -> None:
        self.goal = goal
        self.agent = agent
        self.user = user
        self.tools = agent.get_tools()
        self.max_iteration = max_iteration
        self.completed_actions = completed_actions
        if len(completed_actions) > 0:
            self.last_action = completed_actions[-1]
        else:
            self.last_action = None

    def run(self) -> Any:
        cur_action = None
        iteration_count = 0
        while iteration_count < self.max_iteration:
            cur_action = self._new_action(
                goal=self.goal,
                completed_actions=self.completed_actions,
                last_action=self.last_action,
                tools=self.tools
            )
            print(f"Current Action: {cur_action}\n")
            if cur_action.type == "finish":
                return cur_action.tool_call.result
            self.completed_actions.append(cur_action)
            self.last_action = cur_action
            iteration_count += 1
        

    def _get_chain(self, tools: List[Tool]) -> Runnable:
        create_action_prompt = PromptTemplate(
            template="""
            {agent_role}

            You have the following user info:
            user_id: {user_id}

            You have the following objective:
            `{goal}`.

            You have the following completed tasks:
            `{completed_actions}`

            You just completed the following task:
            `{last_action}`

            Based on this information, use the best tool to make progress or accomplish the task entirely.
            Select the correct function by being smart and efficient. Ensure "reasoning" and only "reasoning" is in the
            {language} language.
            """,
            input_variables=["agent_role", "user_id", "goal", "completed_actions", "last_action", "language"],
        )
        prompt = ChatPromptTemplate.from_messages(
            [SystemMessagePromptTemplate(prompt=create_action_prompt)]
        )
        openai_tools = list(map(lambda x: x.to_openai_tool(), tools))
        llm = get_tool_calling_model().bind(
            tools=openai_tools,
            tool_choice="required"
        )
        chain = prompt | llm
        return chain

    def _new_action(
        self,
        goal: str,
        tools: List[Tool],
        completed_actions: List[AgentAction] = [],
        last_action: Optional[AgentAction] = None
    ) -> AgentAction:
        chain = self._get_chain(tools=tools)
        args = {
            "agent_role": self.agent.role_description,
            "user_id": self.user.id,
            "goal": goal,
            "completed_actions": [action.format_action() for action in completed_actions],
            "last_action": last_action.format_action() if last_action else None,
            "language": "Simplified Chinese"
        }
        message = chain.invoke(args)
        tool_calls = message.additional_kwargs.get("tool_calls", None)
        if tool_calls and len(tool_calls) > 0:
            # TODO: handle parallel tool calls
            tool_call = tool_calls[0]
            function = tool_call["function"]
            tool_name = function["name"]
            tool_args = function["arguments"]
            tool = self.agent.get_tool_from_name(tool_name)
            args = PydanticOutputParser(
                pydantic_object=tool.input_schema
            ).parse(tool_args)
            result = self._call_agent_tool(tool=tool, args=args)
            if args.task_completed == True:
                action_type = "finish"
            else:
                action_type = "run"
            return AgentAction(
                reasoning=args.reasoning,
                type=action_type,
                tool_call=ToolCall(
                    name=tool_name,
                    args=tool_args,
                    result=result
                )
            )
        else:
            return None


    def _call_agent_tool(self, tool: Tool, args: BaseModel) -> Any:
        args_dict = args.dict()
        del args_dict['reasoning']
        del args_dict['task_completed']
        return tool.call(**args_dict)


    