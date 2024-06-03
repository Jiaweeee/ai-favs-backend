from langchain_core.runnables import Runnable
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import logging
import app.utils.llm as LLM

logger = logging.getLogger(__name__)

def create_follow_ups_chain() -> Runnable:
  system_prompt = """
  Given a chat history and the latest user question, \
  please generate a list of no more than 5 potential follow-up questions that could continue the conversation.\
  The aim is to create questions that are relevant, \
  encourage further dialogue, and directly address the user's inquiry. \
  Format the questions in an open-ended manner to allow for more in-depth exploration of the topics.\
  
  chat history: {chat_history} \
  question: {input} \

  The output should be in the format of a json list with the key 'follow_ups' \
  The questions in the json list should be in simplified Chinese. \
  """
  output_parser = JsonOutputParser()
  prompt = PromptTemplate(
    template=system_prompt,
    input_variables=["chat_history", "input"]
  )
  llm = LLM.get_simple_model()
  return prompt | llm | output_parser