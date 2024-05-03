from app.utils.llm import get_llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

RESPONSE_TEMPLATE = """
Please analyze the content provided below and return the following information in simplified Chinese.\

content: {content} \
{format_instructions} \
"""

class AISummary(BaseModel):
  labels: List[str] = Field(description='A list of no more than 5 keywords that are most closely related to the content.')
  summary: str = Field(description='A summary of the content.')
  highlights: List[str] = Field(description='The main points highlighted in the content.')

def create_chain():
  llm = get_llm()
  output_parser = JsonOutputParser(pydantic_object=AISummary)
  prompt = PromptTemplate(
    template=RESPONSE_TEMPLATE,
    input_variables=["content"],
    partial_variables={"format_instructions": output_parser.get_format_instructions()}
  )
  return prompt | llm | output_parser