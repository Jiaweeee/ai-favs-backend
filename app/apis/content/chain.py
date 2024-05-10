from app.utils.llm import get_llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

RESPONSE_TEMPLATE = """
Please analyze the content provided below and return the following information in simplified Chinese.\

content: {content} \

The result you return should be in json format that includes the following keys: \
- labels: A list of no more than 5 keywords that are most closely related to the content. \
- summary: A string of summary of the content. \
- highlights: A list of the main points highlighted in the content. \
"""

def create_chain():
  llm = get_llm()
  output_parser = JsonOutputParser()
  prompt = PromptTemplate(
    template=RESPONSE_TEMPLATE,
    input_variables=["content"],
    partial_variables={"format_instructions": output_parser.get_format_instructions()}
  )
  return prompt | llm | output_parser