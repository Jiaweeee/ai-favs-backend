from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from typing import List
from pydantic import BaseModel, Field
import app.utils.llm as LLM

class TaggingToolOutput(BaseModel):
    tags: List[str] = Field(description="Provide less than 5 keywords related to the content.")

class ClassificationToolOutput(BaseModel):
    name: str = Field(description="The name of the category.")
    description: str = Field(description="The description of the category")

def summary_tool(text: str):
    """Returns the summary of the given text."""
    llm = LLM.get_simple_model(long_context=len(text) > 8192)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize the following text concisely, focusing on the main points and key information."),
        ("user", "{input}")
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"input": text})

def rewrite_tool(text: str, instruction: str):
    """Rewrites the given text according to the instruction"""
    llm = LLM.get_simple_model(long_context=len(text) > 8192)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Rewrite the following text according to the given instruction."),
        ("user", "Instruction: {instruction}"),
        ("user", "Text: {text}")
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"text": text, "instruction": instruction})


def tagging_tool(text: str):
    """Extract keywords from a given text."""
    functions = [
        convert_to_openai_function(TaggingToolOutput)
    ]
    llm = LLM.get_tool_calling_model().bind(
        functions=functions,
        function_call={"name": "TaggingToolOutput"}
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract keywords from the following text. \
            The keywords should represent the main content and core themes of the text."),
        ("user", "{input}")
    ])
    chain = prompt | llm | JsonOutputFunctionsParser()
    return chain.invoke({"input": text})

def classification_tool(text: str, category_names: List[str] = []):
    """Classify the given text into the most relevant category based on its content."""
    functions = [
        convert_to_openai_function(ClassificationToolOutput)
    ]
    llm = LLM.get_tool_calling_model().bind(
        functions=functions,
        function_call={"name": "ClassificationToolOutput"}
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Classify the following text into one of the provided categories. \
            If the text does not fit any existing category, create a new category. \
            The category name you returned should be consice and tidy, with no more than 3 words."),
        ("user", "content: {input}"),
        ("user", "categories: {categories}")
    ])
    chain = prompt | llm | JsonOutputFunctionsParser()
    return chain.invoke({"input": text, "categories": category_names})
