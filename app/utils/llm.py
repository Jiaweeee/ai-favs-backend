from langchain_openai import ChatOpenAI
import enum

class OpenAIModelName(str, enum.Enum):
    GPT3_5_TURBO = "gpt-3.5-turbo"
    GPT3_5_TURBP_16K = "gpt-3.5-turbo-16k"
    GPT4_O = "gpt-4o"

class MoonshotModelName(str, enum.Enum):
    """
    Language models from Moonshot.
    These models does NOT support function calling.
    """
    MOONSHOT_V1_8K = "moonshot-v1-8k"
    MOONSHOT_V1_32K = "moonshot-v1-32k"
    MOONSHOT_V1_128K = "moonshot-v1-128k"

def get_tool_calling_model():
    """
    The returned model is capable of handling complex tasks, like function calling
    or output structured data.
    """
    return ChatOpenAI(model=OpenAIModelName.GPT4_O)

def get_simple_model(long_context: bool = False):
    """
    The model return by this function can only be used for simple tasks, e.g. text generation, text re-writing.
    It should not be used for tasks like function calling or output strucured data.
    For those tasks, use `get_tool_calling_model` instead.
    """
    if long_context:
        model_name = OpenAIModelName.GPT3_5_TURBP_16K
    else:
        model_name = OpenAIModelName.GPT3_5_TURBO
    return ChatOpenAI(model=model_name)
