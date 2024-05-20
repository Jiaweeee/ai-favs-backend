from app.utils.llm import get_llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def create_summary_chain():
  llm = get_llm()
  output_parser = JsonOutputParser()
  prompt_template = """
  Please analyze the content provided below and return the following information in simplified Chinese.\

  content: {content} \

  The result you return should be in json format that includes the following keys: \
  - tags: A list of less than 5 keywords that are most closely related to the content. \
  """
  prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["content"]
  )
  return prompt | llm | output_parser

def create_category_chain():
  llm = get_llm()
  output_parser = JsonOutputParser()
  prompt_template = """
  As an AI assistant, I need your help to categorize a new article into my knowledge base. \
  To do this, I will provide you with the following details about the article and the existing \
  categories within my knowledge base. Your task is to analyze this information and \
  put it into a category that best fit its content. \
  If you think the article does not fit into any of the existing categories, \
  or you think the article should be put into a more relevant category,
  you should create a new category with an appropriate name and description based on the article's content. \
  Please note that even if the existing categories list is empty, you should still create a relevant category based on the article's content. \
  Article info: {item}
  Existing categories in my knowledge base: {categories}

  Please use this information to classify the new article and return the appropriate JSON object. \
  The JSON object should have two fields: \
  - "name": the category name \
  - "description": the category description. \
  
  You should only return the JSON object, nothing else.
  """
  prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["item", "categories"]
  )
  return prompt | llm | output_parser